from typing import Any, NewType, Optional
import arrow
import rich.progress
import ofscraper.utils.constants as constants
from ofscraper.classes.progress.task import Task


TaskID = NewType("TaskID", int)


class MultiprocessProgress(rich.progress.Progress):
    def __init__(self, *args, **kwargs) -> None:
        self._files = {}
        self._last_updated={}
        super().__init__(*args, **kwargs)

    def get_file(self, taskID):
        return self._files.get(taskID)

    def add_task(
        self,
        description: str,
        task_id: str,
        start: bool = True,
        total: Optional[float] = 100.0,
        completed: int = 0,
        visible: bool = True,
        file=None,
        **fields: Any,
    ) -> TaskID:
        """Add a new 'task' to the Progress display.

        Args:
            description (str): A description of the task.
            start (bool, optional): Start the task immediately (to calculate elapsed time). If set to False,
                you will need to call `start` manually. Defaults to True.
            total (float, optional): Number of total steps in the progress if known.
                Set to None to render a pulsing animation. Defaults to 100.
            completed (int, optional): Number of steps completed so far. Defaults to 0.
            visible (bool, optional): Enable display of the task. Defaults to True.
            **fields (str): Additional data fields required for rendering.

        Returns:
            TaskID: An ID you can use when calling `update`.
        """
        with self._lock:
            task = Task(
                task_id,
                description,
                total,
                completed,
                visible=visible,
                fields=fields,
                _get_time=self.get_time,
                _lock=self._lock,
                file=file
            )
            self._tasks[task_id] = task
            self._files[task_id] = file if file else None
            if start:
                self.start_task(task_id)

        self.refresh()
        return task_id


    def update(self,*args,**kwargs):
        task_id=args[0]
        now=arrow.now()
        if not self._check_last_updated(task_id,now=now):
            return
        super().update(*args,**kwargs)
        self._update_last_updated(task_id,now=now)

    def _update_last_updated(self,task_id,now=None):
        now=now or arrow.now()
        self._last_updated[task_id]=now.float_timestamp
    def _check_last_updated(self,task_id,now=None):
        last_updated=self._last_updated.get(task_id)
        if not last_updated:
            return True
        update_freq=constants.getattr("MULTIPROGRESS_JOB_UPDATE_FREQ")
        if ((now or arrow.now()).float_timestamp-last_updated)>update_freq:
            return True
        return False