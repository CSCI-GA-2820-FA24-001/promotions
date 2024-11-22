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
        case 'search':
            endDateInputId = '#search_promotion_end_date';
            break;
        case 'search-range':
            endDateInputId = '#search_promotion_date_range_end';
            break;
        default:
            console.error("Invalid type specified");
            return; // Exit the function if the type is not valid
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
            break;
        default:
            console.error("Invalid type specified");
            return;
    }

    // Select the appropriate start date input element using its ID
    let startDateInput = $(startDateInputId);
    startDateInput.attr('max', endDate);
}

function clearForm(type) {
    console.log('clear form');
    switch (type) {
        case 'create':
            $('#createPromotionForm')[0].reset();
            break;
        case 'search':
            $('#searchPromotionForm')[0].reset();
            break;
        case 'retrieve':
            $('#retrievePromotionForm')[0].reset();
            break;
        case 'delete':
            $('#deletePromotionForm')[0].reset();
            break;
        case 'update':
            $('#updatePromotionForm')[0].reset();
            break;
        default:
            console.error("Invalid form type specified");
    }

    $("#flash_message").empty();
}


