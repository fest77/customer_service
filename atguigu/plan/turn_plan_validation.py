"""
这个模块实现意图识别结果校验，降低LLM幻觉
"""
from atguigu.domain.state import DialogueState
from atguigu.plan.models import TurnPlan, TurnPlanValidationResult, ClarifyReason, TaskTurnPlan
from atguigu.task.command.models import StartFlowCommand, ResumeTaskCommand, CancelTaskCommand
from atguigu.task.flow.models import FlowCatalog


class TurnPlannValidator:

    def validation(self, turnPlan:TurnPlan,
                   state:DialogueState,
                   flow_catalog:FlowCatalog) -> TurnPlanValidationResult:
        # 1 判断意图识别是否识别到多个轨道，比如有闲聊和任务流程
        active_tracks:list[str] = []
        if turnPlan.task is not None:
            active_tracks.append("task")

        if turnPlan.knowledge is not None:
            active_tracks.append("knowledge")

        if turnPlan.chitchat is not None:
            active_tracks.append("chitchat")

        # 判断active_tracks里面轨道数量
        if not active_tracks: # 没有识别内容
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TRACK
            )

        # 识别多个轨道，校验失败
        if len(active_tracks) > 1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TRACKS
            )

        # 获取一条轨道
        active_track = active_tracks[0]
        # 2 如果识别只是一个轨道，根据不同轨道做不同校验
        ## 任务流程专门校验
        if active_track == 'task':
            return self._validator_task_plan(turnPlan.task,
                                             state,flow_catalog)

        ## 知识检索专门校验
        if active_track == 'knowledge':
            # todo
            return self._validator_knowledge_plan()

        return TurnPlanValidationResult(
            valid=True
        )

    # 任务流程校验的方法
    def _validator_task_plan(self,
                             task:TaskTurnPlan,
                             state:DialogueState,
                             flow_catalog:FlowCatalog) -> TurnPlanValidationResult:
        if not task.commands:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.INVALID_TASK_COMMAND
            )
        # 遍历task.commands 得到每个command，判断每个command类型
        # 根据不同类型做不同校验
        for command in task.commands:
            # start_flow   resume_task
            if isinstance(command,StartFlowCommand):
                ### {"command": "start_flow", "flow": "<flow_id>"}
                #### 校验flow_id在yaml文件是否存在
                flow_id = command.flow
                if flow_id not in flow_catalog.flows:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

            if isinstance(command,ResumeTaskCommand):
                ### {"command": "resume_task", "task_id": "<task_id>"},
                #### 判断恢复task_id在state里面中断列表是否存在
                #### 恢复前提条件：有暂停任务
                # 获取要恢复的任务id
                task_id = command.task_id
                # 获取中断列表所有任务id
                # [1,2,3]
                all_paused_ids = [
                       paused.task_id
                    for paused in state.tasks.paused
                ]
                # 判断恢复任务id在列表是否存在
                if task_id not in all_paused_ids:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

            if isinstance(command,CancelTaskCommand):
                ### {"command": "cancel_task", "task_id": "<task_id>"}
                #### 判断取消任务 在 中断列表里面 或者 当前活跃任务是否存在
                # 获取取消任务id
                task_id = command.task_id
                # 把中断列表所有任务id
                all_paused_ids = [
                      paused.task_id
                    for paused in state.tasks.paused
                ]
                # 把当前活跃任务的任务id
                if state.tasks.active:
                    all_paused_ids.append(state.tasks.active.task_id)

                # 判断取消任务id是否存在
                if task_id not in all_paused_ids:
                    return TurnPlanValidationResult(
                        valid=False,
                        reason=ClarifyReason.INVALID_TASK_COMMAND
                    )

        # 注意return true位置，，如果有多个command放到for有问题
        return TurnPlanValidationResult(
            valid=True
        )

    def _validator_knowledge_plan(self):
        return TurnPlanValidationResult(
            valid=True
        )
