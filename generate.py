import ollama

def generate_install_commands(user_os, library, package_manager, version):
    """
    Uses a locally running DeepSeek model from Ollama to generate install commands.
    """
    prompt = (
        f"You are an assistant that generates terminal commands. "
        f"MAKE SURE to put the $ symbol in front of every command NO MATTER WHAT. "
        f"MAKE SURE to put the version as {version} NO MATTER WHAT. "
        f"Provide only the exact commands (one per line) needed to install {library} "
        f"on {user_os} using {package_manager}. Do not include any extra explanation. This should be formatted as lines of text exactly as the appear in terminal with absolultely no other text other than these commands." 
        f"Please do not list with numbers or provide any other text/explanation it should just be the command followed by a new line if there are multiple commands. " 
        f"Having any other text will cause egregious errors in the code and will cause complete system failure. Do not give me any steps only the commands to run in the shell. If version not provided assume latest version. "
        f"Do not use any other package manager other than {package_manager}. "
        f"Do not use any other OS other than {user_os}. "
        f"Do not use any other library other than {library}. "
    )

    response = ollama.chat(model="deepseek-coder:6.7b", messages=[{"role": "user", "content": prompt}])
    #print(response["message"]["content"])
    if "message" in response:
        commands = []
        for message in response["message"]["content"].split("\n"):
            if message.startswith("$ "):
                command = message[2:]
                commands.append(command)
        return commands
    else:
        return "Error: No response from Ollama."

