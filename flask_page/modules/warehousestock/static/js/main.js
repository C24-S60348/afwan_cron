document.addEventListener('DOMContentLoaded', function () {
  // Mobile sidebar toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // Quick fill login credentials
  window.fillCredentials = function (username, password) {
    const userField = document.getElementById('username');
    const passField = document.getElementById('password');
    if (userField && passField) {
      userField.value = username;
      passField.value = password;
      userField.focus();
    }
  };

  // Transfer Modal Data Population
  const transferModal = document.getElementById('transferModal');
  if (transferModal) {
    transferModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;
      const itemId = button.getAttribute('data-item-id');
      const partNo = button.getAttribute('data-part-no');
      const sourceStage = button.getAttribute('data-source-stage');

      const modalItemId = transferModal.querySelector('#transfer_item_id');
      const modalPartNo = transferModal.querySelector('#transfer_part_no');
      const modalSource = transferModal.querySelector('#transfer_source_stage');

      if (modalItemId) modalItemId.value = itemId;
      if (modalPartNo) modalPartNo.textContent = partNo;
      if (modalSource && sourceStage) modalSource.value = sourceStage;
    });
  }

  // MC Plan Modal Data Population
  const updatePlanModal = document.getElementById('updatePlanModal');
  if (updatePlanModal) {
    updatePlanModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;
      const planId = button.getAttribute('data-plan-id');
      const partNo = button.getAttribute('data-part-no');
      const closingCtn = button.getAttribute('data-closing-ctn');
      const forecastM1 = button.getAttribute('data-forecast-m1');
      const forecastM2 = button.getAttribute('data-forecast-m2');

      updatePlanModal.querySelector('#plan_id').value = planId;
      updatePlanModal.querySelector('#plan_part_no').textContent = partNo;
      updatePlanModal.querySelector('#plan_closing_ctn').value = closingCtn || 0;
      updatePlanModal.querySelector('#plan_forecast_m1').value = forecastM1 || 0;
      updatePlanModal.querySelector('#plan_forecast_m2').value = forecastM2 || 0;
    });
  }

  // QA Action Modal Data Population
  const qaActionModal = document.getElementById('qaActionModal');
  if (qaActionModal) {
    qaActionModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;
      const itemId = button.getAttribute('data-item-id');
      const partNo = button.getAttribute('data-part-no');
      const actionType = button.getAttribute('data-action-type');
      const actionTitle = button.getAttribute('data-action-title');

      qaActionModal.querySelector('#qa_item_id').value = itemId;
      qaActionModal.querySelector('#qa_part_no').textContent = partNo;
      qaActionModal.querySelector('#qa_action_type').value = actionType;
      qaActionModal.querySelector('#qa_modal_title').textContent = actionTitle || 'QA Inspection Action';
    });
  }

  // Adjust Stock Modal Data Population
  const adjustStockModal = document.getElementById('adjustStockModal');
  if (adjustStockModal) {
    adjustStockModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;
      const itemId = button.getAttribute('data-item-id');
      const partNo = button.getAttribute('data-part-no');
      const currentWh = button.getAttribute('data-current-wh');

      adjustStockModal.querySelector('#adjust_item_id').value = itemId;
      adjustStockModal.querySelector('#adjust_part_no').textContent = partNo;
      adjustStockModal.querySelector('#adjust_warehouse_ctn').value = currentWh || 0;
    });
  }
});
