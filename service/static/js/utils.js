// This function updates the minimum end date based on the selected end date.
const updateEndDateMin = (startDate, type) => {
    let endDateInputId;

    switch (type) {
        case 'create':
            endDateInputId = '#create_promotion_end_date';
            break;
        case 'update':
            endDateInputId = '#update_promotion_end_date';
            break;
        case 'search-range':
            endDateInputId = '#search_promotion_date_range_end';
            toggleActiveState('search_range');
            break;
        default:
            console.error("Invalid type specified");
            return;
    }

    let endDateInput = $(endDateInputId);
    endDateInput.prop('disabled', false);
    endDateInput.attr('min', startDate);
}

// This function updates the maximum start date based on the selected end date.
const updateStartDateMax = (endDate, type) => {
    let startDateInputId;

    switch (type) {
        case 'create':
            startDateInputId = '#create_promotion_start_date';
            break;
        case 'update':
            startDateInputId = '#update_promotion_start_date';
            break;
        case 'search':
            startDateInputId = 'search_promotion_start_date';
            toggleActiveState('single');
            break;
        default:
            console.error("Invalid type specified");
            return;
    }

    let startDateInput = $(startDateInputId);
    startDateInput.attr('max', endDate);
}

const clearForm = (type) => {
    console.log('clear form');
    switch (type) {
        case 'create':
            $('#createPromotionForm')[0].reset();
            break;
        case 'search':
            $('#searchPromotionForm')[0].reset();
            break;
        case 'delete':
            $('#deletePromotionForm')[0].reset();
            break;
        case 'update':
            $('#updatePromotionForm')[0].reset();
            $('#update_promotion_id').prop('disabled', false);
            break;
        default:
            console.error("Invalid form type specified");
    }

    $("#flash_message").empty();
}

const toggleActiveState = (type) => {
    const allDateInputs = ['#search_promotion_start_date', '#search_promotion_end_date', '#search_promotion_date_range_start', '#search_promotion_date_range_end'];

    let activeInputIDs;

    switch (type) {
        case 'search_start_date':
            activeInputIDs = ['#search_promotion_start_date'];
            StateManager.setDateType('start_date');
            break;
        case 'search_end_date':
            activeInputIDs = ['#search_promotion_end_date'];
            StateManager.setDateType('end_date');
            break;
        case 'search_range':
            activeInputIDs = ['#search_promotion_date_range_start', '#search_promotion_date_range_end'];
            StateManager.setDateType('date_range');
            break;
        default:
            // If no specific type is provided, consider all fields active
            activeInputIDs = allDateInputs;
            break;
    }

    // Clear any previous visual cues from all fields
    $(allDateInputs.join(',')).removeClass('text-muted').css('opacity', 1);

    // Apply visual cues to non-active fields
    allDateInputs.filter(id => !activeInputIDs.includes(id)).forEach(id => {
        $(id).addClass('text-muted').css('opacity', 0.5);
    });

    // Ensure active fields are fully visible
    $(activeInputIDs.join(',')).removeClass('text-muted').css('opacity', 1);
}

const updateFormData = (promotion, type) => {
    switch (type) {
        case 'update-fill':
            const formPrefix = 'update_promotion_';

            $(`#${formPrefix}name`).val(promotion.name);
            $(`#${formPrefix}description`).val(promotion.description);
            $(`#${formPrefix}product_ids`).val(promotion.product_ids.join(', ')); // Assuming product_ids is always an array
            $(`#${formPrefix}start_date`).val(promotion.start_date.slice(0, 10)); // Adjust to match input date format
            $(`#${formPrefix}end_date`).val(promotion.end_date.slice(0, 10)); // Adjust to match input date format
            $(`#${formPrefix}active_status`).val(promotion.active_status.toString());
            $(`#${formPrefix}extra`).val(promotion.extra ? JSON.stringify(promotion.extra, null) : '');
            break;
        default:
            break;
    }
}