import subprocess

def generate_draugr_command(
    server,
    run_folder, 
    order_list, 
    skip_gstore=False, 
    disable_wizard=False, 
    test_mode=False, 
    is_multiome=False, 
    bcl_flags=None, 
    cellranger_flags=None, 
    bases2fastq_flags=None
):
    """
    Generate a command string for the Draugr pipeline.

    Args:
        server (str): Server location
        run_folder (str): Run folder name.
        order_list (list): List of order IDs to process.
        skip_gstore (bool): Skip the Gstore copy step.
        disable_wizard (bool): Disable the wizard.
        test_mode (bool): Enable test mode.
        is_multiome (bool): Enable multiome mode.
        bcl_flags (str): Custom Bcl2fastq flags.
        cellranger_flags (str): Custom Cellranger flags.
        bases2fastq_flags (str): Custom Bases2fastq flags.

    Returns:
        str: Command string for the Draugr pipeline.
    """
    draugr_command = f"python /export/local/analyses/draugr_exec/draugr.py --login-config /home/illumina/bfabric_cred/.bfabricpy.yml --run-folder /export/local/data/{run_folder} --analysis-folder /export/local/analyses --logger-rep /srv/GT/analysis/falkonoe/dmx_logs/prod --scripts-destination /srv/GT/analysis/datasets"

    TEST_COMMAND = f"python /export/local/analyses/draugr_exec/draugr.py --login-config /home/illumina/bfabric_cred/.bfabricpy.yml --run-folder /export/local/data/20240625_FS10002953_30_BTC69705-1710 --analysis-folder /export/local/analyses --logger-rep /srv/GT/analysis/falkonoe/dmx_logs/prod --scripts-destination /srv/GT/analysis/datasets --skip-gstore-copy --disable-wizard"
    TEST_SERVER = "fgcz-s-025"

    if skip_gstore:
        draugr_command += " --skip-gstore-copy"
    if disable_wizard:
        draugr_command += " --disable-wizard"
    if test_mode:
        # draugr_command += " --test-mode"
        draugr_command += ""
    if is_multiome:
        draugr_command += " --is-multiome-run"
    if bcl_flags:
        draugr_command += " --custom-bcl2fastq-flags " + bcl_flags
    if cellranger_flags:
        draugr_command += " --custom-cellranger-flags " + cellranger_flags
    if bases2fastq_flags:
        draugr_command += " --custom-bases2fastq_flags " + bases2fastq_flags
    
    draugr_command += " --reprocess-orders " + ",".join([str(elt) for elt in order_list])

    SET_ENVIRON = "export OPENBLAS_NUM_THREADS=1 && export OPENBLAS_MAIN_FREE=1 &&"
    LMOD_SETUP = "source /usr/local/ngseq/etc/lmod_profile && export MODULEPATH=/usr/local/ngseq/etc/modules &&"
    # CONDA_SETUP = ". /usr/local/ngseq/miniconda3/etc/profile.d/conda.sh && conda activate gi_py3.11.5 &&"
    CONDA_SETUP = "module load Dev/Python && conda activate gi_py3.11.5 &&"
    MODULE_LOAD = "module load Tools/bcl2fastq && module load Aligner/CellRanger && module load Aligner/CellRangerARC && module load Tools/Bases2Fastq"

    PREFIX = f"{SET_ENVIRON} {LMOD_SETUP} {CONDA_SETUP} {MODULE_LOAD}"

    system_call = f"ssh illumina@{server} '{PREFIX} && nohup {draugr_command} &> /export/local/data/draugrUI/output.log &' &> output.log"
    TEST_SYSTEM_CALL = f"ssh illumina@{TEST_SERVER} '{PREFIX} && nohup {TEST_COMMAND} &> /export/local/data/draugrUI/output.log &' &> output.log"

    # return system_call
    return system_call

def check_if_file_exists(ssh_command):
    try:
        subprocess.check_output(ssh_command, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def generate_sushi_command(
    order_list, 
    run_name
):
    
    """
    Generate a command string for the Sushi pipeline.

    Args:
        order_list (list): List of order IDs to process.
        run_name (str): Run name.

    Returns:
        str: Command string for the Sushi pipeline.
    """

    ssh_login = "trxcopy@fgcz-h-031"
    remote_path = "/srv/GT/analysis/datasets"

    check_file_command_original = f"ssh {ssh_login} 'ls {remote_path}/{run_name}*'"  
    check_file_command_processed = f"ssh {ssh_login} 'ls {remote_path}/processed/{run_name}*'"

    in_orig = check_if_file_exists(check_file_command_original)
    in_proc = check_if_file_exists(check_file_command_processed)

    if not in_orig and not in_proc:
        return False
    
    order_string = "|".join([str(elt) for elt in order_list]).replace("|", "\\|")

    if in_orig:
        ssh_command = f'''ssh trxcopy@fgcz-h-031 "nohup bash -lc 'cd /srv/sushi/production/master && grep '{order_string}' /srv/GT/analysis/datasets/{run_name}* | uniq -u | bash -s &> /srv/GT/analysis/datasets/draugrUI/output.log &' &> output.log"'''
    else:
        ssh_command = f'''ssh trxcopy@fgcz-h-031 "nohup bash -lc 'cd /srv/sushi/production/master && grep '{order_string}' /srv/GT/analysis/datasets/processed/{run_name}* | uniq -u | bash -s &> /srv/GT/analysis/datasets/draugrUI/output.log &' &> output.log"'''
    return ssh_command
