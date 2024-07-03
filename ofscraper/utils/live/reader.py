
import ofscraper.utils.live.progress as progress_utils
import ofscraper.utils.settings as settings
def get_multi_download_curr_jobs_speed_bars():
    if settings.get_download_bars():
        return sum([ele.speed or  0 for ele in progress_utils.multi_download_job_progress.tasks])
    return sum([ele.speed_via_file or  0 for ele in progress_utils.multi_download_job_progress.tasks])