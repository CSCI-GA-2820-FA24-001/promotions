$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function togglePromotionStatus(promotionId, currentStatus) {
        let newStatus = !currentStatus;
        let action = newStatus ? "activate" : "deactivate";
        $.ajax({
            type: "PATCH",
            url: `/promotions/${promotionId}/${action}`,
            contentType: "application/json",
            data: JSON.stringify({ active_status: newStatus }),
            success: function () {
                flash_message("Success");
            },
            error: function (error) {
                console.error("Error updating promotion:", error);
                alert("Failed to update the promotion. Please try again.");
            }
        });
    }

    function renderPromotionData(promotions, table) {
        let tableBody = $(`#${table} tbody`);
        tableBody.empty();  // Clear existing data
        promotions.forEach(promotion => {
            // Populate the table with the retrieved promotion data
            let activeText = promotion.active_status ? "Deactivate" : "Activate";
            const row = `
                <tr id="row-${promotion.id}">
                    <td>${promotion.id}</td>
                    <td>${promotion.name}</td>
                    <td>${promotion.description}</td>
                    <td>${promotion.product_ids}</td>
                    <td>${promotion.start_date}</td>
                    <td>${promotion.end_date}</td>
                    <td class="status-cell">${promotion.active_status ? 'Active' : 'Inactive'} 
                        <button 
                            class="btn btn-sm btn-toggle" 
                            id="toggle-btn"
                            data-id="${promotion.id}" 
                            data-status="${promotion.active_status}">
                            ${activeText}
                        </button>
                    </td>
                    <td>${promotion.created_by}</td>
                    <td>${promotion.updated_by}</td>
                    <td>${promotion.created_at}</td>
                    <td>${promotion.updated_at}</td>
                    <td>${JSON.stringify(promotion.extra)}</td>
                        
            </tr>
            `;
            tableBody.append(row);

            $(`#${table}`).on("click", ".btn-toggle", function () {
                console.log('clicked')
                let promotionId = $(this).data("id");
                let currentStatus = $(this).data("status");

                let newStatus = !currentStatus;
                let newStatusText = newStatus ? "Active" : "Inactive";
                let newButtonText = newStatus ? "Deactivate" : "Activate";

                let statusCell = $(this).closest(".status-cell");
                statusCell.html(`
                ${newStatusText} 
                <button 
                    class="btn btn-sm btn-toggle"
                    id="toggle-btn" 
                    data-id="${promotionId}" 
                    data-status="${newStatus}">
                    ${newButtonText}
                </button>
            `);

                togglePromotionStatus(promotionId, currentStatus);
            });
        })
    }

    // ****************************************
    // Create a Promotion
    // ****************************************
    $('#createPromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior

        let id_prefix = "create_";

        let name = $(`#${id_prefix}promotion_name`).val();
        let product_ids = $(`#${id_prefix}promotion_product_ids`).val();
        let start_date = $(`#${id_prefix}promotion_start_date`).val();
        let end_date = $(`#${id_prefix}promotion_end_date`).val();
        let active_status = $(`#${id_prefix}promotion_active_status`).val() == "Active";
        let creator = $(`#${id_prefix}promotion_creator`).val();
        let updater = $(`#${id_prefix}promotion_updater`).val();
        let extra = $(`#${id_prefix}promotion_extra`).val();

        extra = extra === "" ? "{}" : extra;

        let data = {
            name,
            product_ids: product_ids.split(",").map(_ => _.trim()),
            start_date,
            end_date,
            active_status,
            created_by: creator,
            updated_by: updater,
            extra: JSON.parse(extra),
        };

        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            flash_message(`Promotion created successfully. The Promotion ID is ${res.id}`)
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message.replace('"', ""))
        });
    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************
    $('#retrieve-btn').on('click', function (e) {
        e.preventDefault();  // Prevent default form submission behavior

        // retrieve a promotion
        let promotion_id = $("#update_promotion_id").val();

        console.log(`retrieve promotion with id ${promotion_id}`);

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            console.log('retrieve res', res);
            StateManager.setCreator(res.created_by);
            StateManager.setUpdater(res.updated_by);
            $('#update_promotion_id').prop('disabled', true);
            updateFormData(res, 'update-fill');
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Search Promotions
    // ****************************************
    $('#searchPromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior

        // Retrieve form data
        const id_prefix = "search_promotion_";

        const id = $(`#${id_prefix}id`).val();

        const name = $(`#${id_prefix}name`).val();
        const product_id = $(`#${id_prefix}product_id`).val();


        const created_by = $(`#${id_prefix}creator`).val();
        const updated_by = $(`#${id_prefix}updater`).val();
        const active_status = $(`#${id_prefix}active_status`).val();


        const data = {
            name,
            product_id,
            created_by,
            updated_by,
            active_status
        };

        for (const [key, value] of Object.entries(data)) {
            if (!value) {
                console.log('removed field:', key, value);
                delete data[key];
            }
        }

        // Check the current date type from the StateManager
        const dateType = StateManager.getDateType();

        const end_date = $(`#${id_prefix}end_date`).val();
        const exact_match_end_date = $(`#${id_prefix}exact_match_end_date`).prop('checked');

        const date_range_start = $(`#${id_prefix}date_range_start`).val();
        const date_range_end = $(`#${id_prefix}date_range_end`).val();

        const start_date = $(`#${id_prefix}start_date`).val();
        const exact_match_start_date = $(`#${id_prefix}exact_match_start_date`).prop('checked');


        switch (dateType) {
            case 'start_date':
                data.start_date = start_date;
                data.exact_match_start_date = exact_match_start_date;
                break;
            case 'end_date':
                data.end_date = end_date;
                data.exact_match_end_date = exact_match_end_date;
                break;
            case 'date_range':
                data.start_date = date_range_start;
                data.end_date = date_range_end;
                break;
            default:
                break;
        }

        console.log('data', data);

        const baseUrl = id ? `/promotions/${id}` : '/promotions';
        const queryString = id ? '' : $.param(data);  // Only add query string if not searching by ID


        const ajax = $.ajax({
            type: "GET",
            url: `${baseUrl}?${queryString}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            if (!Array.isArray(res)) {
                res = [res]; // Wrap the single object in an array
            }

            renderPromotionData(res, 'promotion-data');
            if (res.length === 0) {
                flash_message("No promotions found");
            } else {
                flash_message("Search successful!");
            }
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    });


    // ****************************************
    // Update A Promotion
    // ****************************************
    $('#updatePromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior
        let id_prefix = "update_";

        let promotion_id = $(`#${id_prefix}promotion_id`).val();
        let name = $(`#${id_prefix}promotion_name`).val().trim();
        let description = $(`#${id_prefix}promotion_description`).val().trim();
        let product_ids = $(`#${id_prefix}promotion_product_ids`).val().trim();
        let start_date = $(`#${id_prefix}promotion_start_date`).val();
        let end_date = $(`#${id_prefix}promotion_end_date`).val();
        let created_by = StateManager.getCreator();
        let updated_by = StateManager.getUpdater();
        let active_status = $(`#${id_prefix}promotion_active_status`).val() == "Active";
        let extra = $(`#${id_prefix}promotion_extra`).val().trim();

        extra = extra === "" ? "{}" : extra;

        data = {
            promotion_id,
            name,
            description,
            start_date,
            end_date,
            active_status,
            created_by,
            updated_by,
            product_ids,
            extra: JSON.parse(extra),
        }

        for (const [key, value] of Object.entries(data)) {
            if (value !== false && !value) {
                console.log('removed field:', key, value);
                delete data[key];
            }
        }

        console.log('updated data', data);

        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "PUT",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function (res) {
            console.log('updated res', res);
            flash_message("Update successful!");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Delete a Promotion
    // ****************************************
    $('#deletePromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior

        let promotion_id = $("#delete_promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            flash_message("Promotion has been Deleted!");
        });

        ajax.fail(function (res) {
            clearForm('delete')
            flash_message(res.responseJSON.message)
        });
    });

});
