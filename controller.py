import subprocess

def run_scripts(scripts, output_file):
    # Open the output file in write mode
    with open(output_file, 'w') as f:
        for script in scripts:
            print(f"Running {script}...")
            f.write(f"Running {script}...\n")

            result = subprocess.run(
                ['python', script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Capture stderr as well
                text=True
            )

            
            # Write both stdout and stderr to the log file
            f.write(result.stdout)
            f.write(result.stderr)  # Include stderr in the logs

            # Check for errors
            if result.returncode != 0:
                error_message = f"{script} exited with return code {result.returncode}\n"
                print(error_message)
                f.write(error_message)
                # Optionally, handle the error or stop execution
                # break
            else:
                success_message = f"{script} completed successfully.\n"
                print(success_message)
                f.write(success_message)

if __name__ == '__main__':
    scripts_to_run = ['santaClaus.py','module.py', 'list.py', 'blueprint.py']
    output_filename = 'output.txt'
    run_scripts(scripts_to_run, output_filename)
