from celery import chain, group, chord
from enterprise_tasks import process_order_workflow, send_realtime_notifications

def start_order_workflow(order_id: int):
    # Example: process order -> send confirmation
    workflow = chain(process_order_workflow.s(order_id), send_realtime_notifications.s({"type":"order_complete"}))
    return workflow.apply_async()
