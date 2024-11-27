$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_product_id").val(res.product_id);
        $("#promotion_start_date").val(res.start_date);
        $("#promotion_end_date").val(res.end_date);
        $("#promotion_date_range_start").val(res.date_range_start);
        $("#promotion_date_range_end").val(res.date_range_end);
        $("#promotion_active_status").val(res.active_status.toString());
        $("#promotion_creator").val(res.creator);
        $("#promotion_updater").val(res.updater);
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Init
    // ****************************************
    $('#promotion-data').hide();


    // ****************************************
    // Tab Event Handler 
    // ****************************************
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var activeTab = $(e.target).attr('href'); // Get the current active tab

        const tabsToShowTable = ['#search', '#retrieve'];

        if (tabsToShowTable.includes(activeTab)) {
            $('#promotion-data').show();
        } else {
            $('#promotion-data').hide();
        }
    });

    function render_promotion_data(promotions, table) {
        let tableBody = $(`#${table} tbody`);
        tableBody.empty();  // Clear existing data

        promotions.forEach(promotion => {
            // Populate the table with the retrieved promotion data
            const row = `
                <tr>
                    <td>${promotion.id}</td>
                    <td>${promotion.name}</td>
                    <td>${promotion.description}</td>
                    <td>${promotion.product_ids}</td>
                    <td>${promotion.start_date}</td>
                    <td>${promotion.end_date}</td>
                    <td>${promotion.active_status ? 'Active' : 'Inactive'}</td>
                    <td>${promotion.created_by}</td>
                    <td>${promotion.updated_by}</td>
                    <td>${promotion.created_at}</td>
                    <td>${promotion.updated_at}</td>
                    <td>${JSON.stringify(promotion.extra)}</td>
                </tr>
            `;
            tableBody.append(row);
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
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message.replace('"', ""))
        });
    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************
    $('#retrievePromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior
        // retrieve a promotion
        let promotion_id = $("#retrieve_promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            // update_form_data(res)
            render_promotion_data([res], 'promotion-data');
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clearForm('retrieve')
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

        // Constructing query string from data object
        const queryString = $.param(data);

        const ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
        });

        ajax.done(function (res) {
            console.log('res', res);
            render_promotion_data(res, 'search-promotion-data');
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
        let name = $(`#${id_prefix}promotion_name`).val();
        let description = $(`#${id_prefix}promotion_description`).val();
        let product_ids = $(`#${id_prefix}promotion_product_ids`).val();
        let start_date = $(`#${id_prefix}promotion_start_date`).val();
        let end_date = $(`#${id_prefix}promotion_end_date`).val();
        let created_by = $(`#${id_prefix}promotion_creator`).val();
        let updated_by = $(`#${id_prefix}promotion_updator`).val();
        let active_status = $(`#${id_prefix}promotion_active_status`).val() == "Active";

        data = {
            promotion_id,
            name,
            description,
            start_date,
            end_date,
            active_status,
            created_by,
            updated_by,
            product_ids
        }
        console.log(data)
        // for (const [key, value] of Object.entries(data)) {
        //     if (!value) {
        //         console.log('removed field:', key, value);
        //         delete data[key];
        //     }
        // }

        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "PUT",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function (res) {
            console.log('res', res);
            if (res.length === 0) {
                flash_message("No promotions found");
            } else {
                flash_message("Update successful!");
            }
        });

        ajax.fail(function (res) {
            clearForm('update')
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Delete a Promotion
    // ****************************************
    $('#deletePromotionForm').on('submit', function (e) {
        console.log('delete form');
        e.preventDefault();  // Prevent default form submission behavior
        // TODO : delete a promotion
    });

})
