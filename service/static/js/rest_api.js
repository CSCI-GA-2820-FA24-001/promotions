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

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_id").val("");
        $("#promotion_name").val("");
        $("#promotion_product_id").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_date_range_start").val("");
        $("#promotion_date_range_end").val("");
        $("#promotion_active_status").val("");
        $("#promotion_creator").val("");
        $("#promotion_updater").val("");
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

    function render_promotion_data(promotion) {
        let tableBody = $("#promotion-data tbody");
        tableBody.empty();  // Clear existing data

        // Populate the table with the retrieved promotion data
        let row = `
            <tr>
                <td>${promotion.id}</td>
                <td>${promotion.name}</td>
                <td>${promotion.description}</td>
                <td>${promotion.product_ids}</td>
                <td>${promotion.start_date}</td>
                <td>${promotion.end_date}</td>
                <td>${promotion.active_status ? 'Active' : 'Inactive'}</td>
                <td>${promotion.creator}</td>
                <td>${promotion.updater}</td>
                <td>${promotion.created_at}</td>
                <td>${promotion.updated_at}</td>
                <td>${JSON.stringify(promotion.extra)}</td>
            </tr>
        `;
        tableBody.append(row);
    }


    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-btn").click(function () {
        clear_form_data()
        $("#flash_message").empty();
    });


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

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
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

        ajax.done(function(res){
            //alert(res.toSource())
            console.log(res)
            // update_form_data(res)
            render_promotion_data(res);
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Search Promotions
    // ****************************************
    $('#searchPromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior
        // TODO : search promotions
    });

    // ****************************************
    // Update A Promotion
    // ****************************************
    $('#updatePromotionForm').on('submit', function (e) {
        e.preventDefault();  // Prevent default form submission behavior
        // TODO : update a promotion
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
