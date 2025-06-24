from gandalf_workshop.workshop_manager import WorkshopManager


def test_manager_methods():
    manager = WorkshopManager()
    assert manager is not None
    manager.commission_new_blueprint()
    manager.request_product_generation_or_revision()
    manager.initiate_quality_inspection()
    manager.finalize_commission_and_deliver()
    manager.request_blueprint_revision()
