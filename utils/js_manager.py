import os, sys, subprocess, re, json, asyncio, argparse


def find_project_files():
    dirs = [os.getcwd(), os.path.dirname(os.getcwd())]
    scripts_dirs = [os.path.join(d, 'scripts') for d in dirs] + dirs
    scripts_dir = next((p for p in scripts_dirs if os.path.exists(p) and os.path.isdir(p)), None)

    paths = {}
    for fname in ['config.js', 'token-info.json']:
        paths[fname] = next(
            (os.path.join(d, fname) for d in [*dirs, scripts_dir] if d and os.path.exists(os.path.join(d, fname))),
            None)

    print(
        f"Found paths: scripts_dir: {scripts_dir}, config.js: {paths['config.js']}, token-info.json: {paths['token-info.json']}")
    return paths['config.js'], paths['token-info.json'], scripts_dir


def get_token_info():
    try:
        _, token_path, _ = find_project_files()
        print(f"🔍 Searching for token-info.json: {token_path}")
        if token_path and os.path.exists(token_path):
            with open(token_path, 'r', encoding='utf-8') as f:
                token_info = json.load(f)
            print(f"✅ token-info.json found and read: {token_info.get('name', 'Unknown')}")
            return token_info
        else:
            print("❌ token-info.json not found")
            return None
    except Exception as e:
        print(f"❌ Error reading token info: {e}")
        return None


async def _process_output(process, log_callback=None, is_async=True):
    stdout_lines = []
    stderr_lines = []

    while True:
        if is_async:
            line = await process.stdout.readline()
            if not line: break
            text = line.decode('utf-8', errors='replace').strip()
        else:
            text = process.stdout.readline()
            if text == '' and process.poll() is not None: break
            text = text.strip()

        if text:
            print(text)
            stdout_lines.append(text)
            if log_callback:
                await log_callback(text) if is_async else log_callback(text)

    stderr = await process.stderr.read() if is_async else process.stderr.read()
    if stderr:
        error_text = stderr.decode('utf-8', errors='replace') if is_async else stderr
        error = f"STDERR: {error_text}"
        print(error)
        stderr_lines.append(error_text)
        if log_callback:
            await log_callback(error) if is_async else log_callback(error)

    return stdout_lines, stderr_lines


async def run_js_file_async(js_file, params=None, log_callback=None):
    try:
        cmd = ['node', js_file]
        if params:
            cmd.extend(['--params', json.dumps(params)])

        print(f"🚀 Running command: {' '.join(cmd)}")
        if log_callback:
            await log_callback(f"Running file: {js_file}" + (f" with params: {params}" if params else ""))

        process = await asyncio.create_subprocess_exec(*cmd,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.PIPE,
                                                       universal_newlines=False)

        stdout_lines, stderr_lines = await _process_output(process, log_callback, True)
        return_code = await process.wait()

        print(f"📊 Execution result:")
        print(f"   - Return code: {return_code}")
        print(f"   - Stdout lines: {len(stdout_lines)}")
        print(f"   - Stderr lines: {len(stderr_lines)}")

        if log_callback:
            await log_callback(f"JavaScript return code: {return_code}")
            if stderr_lines:
                await log_callback(f"STDERR contains {len(stderr_lines)} error lines")

        success = return_code == 0
        print(f"✅ Success: {success}" if success else f"❌ Failure: {success}")
        return success

    except Exception as e:
        error_msg = f"❌ Error running {js_file}: {e}"
        print(error_msg)
        if log_callback: await log_callback(error_msg)
        return False


def run_js_file(js_file, params=None, log_callback=None):
    try:
        cmd = ['node', js_file]
        if params:
            cmd.extend(['--params', json.dumps(params)])

        print(f"🚀 Running command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding='utf-8', errors='replace', universal_newlines=True)

        stdout_lines, stderr_lines = asyncio.run(_process_output(process, log_callback, False))
        return_code = process.poll()

        print(f"📊 Execution result:")
        print(f"   - Return code: {return_code}")
        print(f"   - Stdout lines: {len(stdout_lines)}")
        print(f"   - Stderr lines: {len(stderr_lines)}")

        success = return_code == 0
        print(f"✅ Success: {success}" if success else f"❌ Failure: {success}")
        return success

    except Exception as e:
        error_msg = f"❌ Error running {js_file}: {e}"
        print(error_msg)
        if log_callback: log_callback(error_msg)
        return False


async def _run_scripts(action=None, params=None, log_callback=None, is_async=True):
    _, _, scripts_dir = find_project_files()
    if not scripts_dir:
        msg = "❌ Scripts directory not found"
        print(msg)
        if log_callback:
            await log_callback(msg) if is_async else log_callback(msg)
        return False

    js_files = {
        'create': 'solana-token.js', 'upload': 'ipfs-upload.js', 'metadata': 'metadata.js',
        'revoke': 'revoke-authorities.js', 'distribute': 'washout-tokens.js'
    }

    action_files = {k: os.path.join(scripts_dir, v) for k, v in js_files.items()
                    if os.path.exists(os.path.join(scripts_dir, v))}

    try:
        if action:
            actions = list(action_files.keys()) if action == 'all' else [action] if action in action_files else []
        else:
            parser = argparse.ArgumentParser()
            parser.add_argument('actions', nargs='+', choices=[*action_files.keys(), 'all'])
            args = parser.parse_args()
            actions = list(action_files.keys()) if 'all' in args.actions else args.actions

        print(f"🎯 Actions to execute: {actions}")

        for act in actions:
            if act not in action_files:
                msg = f"❌ Action '{act}' not executed: file not found"
                print(msg)
                if log_callback:
                    await log_callback(msg) if is_async else log_callback(msg)
                continue

            js_file = action_files[act]
            msg = f"\n--- Running: {act} ({js_file}) ---"
            print(msg)
            if log_callback:
                await log_callback(msg) if is_async else log_callback(msg)

            print(f"📂 Checking file: {js_file}")
            print(f"   - File exists: {os.path.exists(js_file)}")
            if params:
                print(f"📋 Parameters: {json.dumps(params, ensure_ascii=False, indent=2)}")

            if is_async:
                result = await run_js_file_async(js_file, params, log_callback)
            else:
                result = run_js_file(js_file, params, log_callback)

            print(f"🎯 Action '{act}' result: {result}")

            if not result:
                msg = f"❌ Action '{act}' failed"
                print(msg)
                if log_callback:
                    await log_callback(msg) if is_async else log_callback(msg)
                return False
            else:
                msg = f"✅ Action '{act}' completed successfully"
                print(msg)

        print("🎉 All actions completed successfully")
        return True

    except Exception as e:
        msg = f"❌ Critical error executing scripts: {e}"
        print(msg)
        if log_callback:
            await log_callback(msg) if is_async else log_callback(msg)
        return False


def run_scripts(action=None, params=None, log_callback=None):
    return asyncio.run(_run_scripts(action, params, log_callback, False))


async def run_scripts_async(action=None, params=None, log_callback=None):
    return await _run_scripts(action, params, log_callback, True)


if __name__ == "__main__":
    run_scripts()