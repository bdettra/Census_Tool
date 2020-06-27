$(document).ready(function () {

    var ShowEngagementForm = function () {
        console.log("ShowForm Activated");
        var btn = $(this);

        $.ajax({
            url: btn.attr("data-url"),

            type: 'get',

            dataType: 'json',

            beforeSend: function () {
                $('#modal-new_engagement').modal('show');
            },

            success: function (data) {
                $('#modal-new_engagement .modal-content').html(data.html_form);
            }
        });
    }

    var SaveEngagementForm = function () {
        console.log("Save form function activted");
        var form = $(this);
        console.log('Working');
        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {

                    $('#engagement_table tbody').html(data.engagements)

                    $('#modal-new_engagement').modal('hide');
                    console.log('Working');
                }
                else {
                    $('#modal-new_engagement .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    }


    var ShowForm = function () {
        console.log("ShowForm Activated");
        var btn = $(this);

        $.ajax({
            url: btn.attr("data-url"),

            type: 'get',

            dataType: 'json',

            beforeSend: function () {
                $('#modal-new_client').modal('show');
            },

            success: function (data) {
                $('#modal-new_client .modal-content').html(data.html_form);
            }
        });
    };

    var SaveForm = function () {
        console.log("Save form function activted");
        var form = $(this);

        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {

                    $('#client_table tbody').html(data.clients)

                    $('#modal-new_client').modal('hide');
                    console.log('Working');
                }
                else{
                    $('#modal-new_client .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    }

    // Create Client
    $(".show-form").click(ShowForm);
    $("#modal-new_client").on("submit", ".create-form", SaveForm);


    // Create Engagement
    $(".show-form").click(ShowEngagementForm);
    $("#modal-new_engagement").on("submit", ".create-form", SaveEngagementForm);


    //Update Client
    $('#client_list').on("click", ".show-form-update", ShowForm);
    $("#modal-new_client").on("submit", ".update-form", SaveForm);

    //Update Engagement
    $('#engagement_list').on("click", ".show-form-update", ShowEngagementForm)
    $("#modal-new_engagement").on("submit", ".update-form", SaveEngagementForm);



});

