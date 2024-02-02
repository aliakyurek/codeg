import gradio as gr
import yaml
from huggingface_hub import hf_hub_download
import os
from llama_cpp import Llama
import consts


def build_gradio_app():
    def build_gradio_sidebar():
        gr.Markdown('''
        ## About
        This app is an LLM-powered code generator built using HuggingFace🤗 ecosystem and:
        - [Awesome LLMs](https://github.com/Hannibal046/Awesome-LLM)
        - [Quantization by TheBloke](https://huggingface.co/TheBloke)
        - [Python for llama.cpp](https://github.com/abetlen/llama-cpp-python)
        - [gradio](https://gradio.app/)

        Checkout coder leaderboards
        - [HF Big Code Models](https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard)
        - [EvalPlus](https://evalplus.github.io/leaderboard.html)

        Made with 💗
        '''.strip())

    def gr_go_onclick(language, task):
        if not language or not task:
            return gr.Row(), gr.Row(), gr.Code()

        if (language := language.lower()) not in gr.Code.languages:
            language = None
        return gr.Row(visible=False), gr.Row(visible=True), gr.Code(language=language)

    def gr_go_onclick_async(language, task):
        if not language or not task:
            yield "", "", ""
        else:
            resp, code = "", ""
            for resp, code, _ in generate_code(language, task=task):
                yield resp, code, ""
            yield resp, code, gr.Textbox(visible=True, interactive=True)

    def gr_usermsg_onsubmit():
        return gr.Textbox(interactive=False)

    def gr_usermsg_onsubmit_async(language, task, code, msg):
        resp = ""
        for resp, code, _ in generate_code(language=language, task=task, code=code, msg=msg):
            yield resp, code
        yield resp, code

    def gr_usermsg_onpostsubmit():
        return gr.Textbox(value="", interactive=True)

    block_params = {
        "title": "Code G.",
        "css": "#_response { border-width: 1px !important; padding: 10px !important;}",
        "js": """
        () => {
            document.body.classList.toggle('dark');
        }"""
    }
    with gr.Blocks(**block_params) as app:
        with gr.Row():
            with gr.Column(scale=1):
                build_gradio_sidebar()
            with gr.Column(scale=5):
                with gr.Row() as gr_boot_pane:
                    with gr.Column(scale=1):
                        pass
                    with gr.Column(scale=2):
                        gr.Markdown('''
                        ## Start
                        Select a programming language, describe the task, improve the code by chatting with AI.
                        '''.strip())
                        with gr.Group():
                            gr_lang = gr.Dropdown(choices=consts.LANGS, label="Language")
                            gr_task = gr.Textbox(label="Task")
                            gr_go = gr.Button(value="Go")
                        gr.Examples([
                            ["Python", "calculate sum of squares of a list"],
                            ["JavaScript", "create a circle class with area calculation method"],
                            ["C", "A stack structure using struct and its methods"],
                            ], inputs=[gr_lang, gr_task])

                    with gr.Column(scale=1):
                        pass
                with gr.Row(visible=False, equal_height=True) as gr_chatncode_pane:
                    with gr.Column(scale=1):
                        gr_response = gr.Markdown(label="Response", elem_id="_response")
                        gr_improve = gr.Textbox(label="Improve", visible=False, placeholder="e.g. use loop instead of recursion")
                    with gr.Column(scale=1):
                        gr_code = gr.Code(label="Code")
        # event handlers
        gr_improve.submit(fn=gr_usermsg_onsubmit, outputs=[gr_improve], queue=False).\
            then(fn=gr_usermsg_onsubmit_async, inputs=[gr_lang, gr_task, gr_code, gr_improve],
                 outputs=[gr_response, gr_code]).\
            then(fn=gr_usermsg_onpostsubmit, outputs=[gr_improve], queue=False)

        gr_go.click(fn=gr_go_onclick, inputs=[gr_lang, gr_task],
                    outputs=[gr_boot_pane, gr_chatncode_pane, gr_code], queue=False).\
            then(gr_go_onclick_async, inputs=[gr_lang, gr_task], outputs=[gr_response, gr_code, gr_improve])
    return app


def generate_code(language=None, task=None, code=None, msg=None):
    if msg is None:
        prompt = consts.INITIAL_PROMPT.format(language=language, task=task)
    else:
        prompt = consts.MODIFY_PROMPT.format(language=language, task=task, code=code, msg=msg)

    stream = llm(prompt, max_tokens=None, echo=False, stream=True)

    resp = ""
    code = ""
    skip_empty = True
    in_code = False
    itr = iter(stream)
    while c := next(itr, False):
        token = c['choices'][0]['text']
        if skip_empty and (token == '\n' or token == ' '):
            continue
        skip_empty = False
        if token == '```':
            next(itr, False)  # skip lang or empty
            in_code = not in_code
            continue

        if in_code:
            code += token
        else:
            resp += token
        yield resp, code, ""


if __name__ == '__main__':
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    with open(consts.CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)

    repo_id = config['model']['repo_id']
    model_file_name = f"{config['model']['prefix']}_{config['model']['variant']}.gguf"
    model_path = os.path.join(consts.MODEL_DIR, model_file_name)

    if not os.path.exists(model_path):
        print("Model not available at local, will be downloaded.")
        hf_hub_download(repo_id=f"{repo_id}", filename=model_file_name, local_dir=consts.MODEL_DIR)

    print("Instantiating model.")
    llm = Llama(model_path=model_path, verbose=config['model']['verbose'], n_ctx=config['model']['context_length'])
    print("Starting UI.")
    build_gradio_app().queue().launch(quiet=True, inbrowser=True, favicon_path= "favicon.ico")
