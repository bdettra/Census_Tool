$(document).ready(function () {
    //Defining the Show Engagement Form Variable

    function ShowModalForm(modal_id){
        console.log(modal_id.data);
        var btn = $(this);

        $.ajax({
            url: btn.attr("data-url"),
            
            type: 'get',

            dataType: 'json',

            beforeSend: function () {
                
                $(modal_id.data).modal('show');
                
            },

            success: function (data) {
                
                $(modal_id.data +  ' .modal-content').html(data.html_form);
            }
        });
    };

    function SaveModalFormTable(html_data){
        var form = $(this);
        console.log(html_data)
        table_id = html_data.data[0];
        modal_id = html_data.data[1];

        console.log(html_data[0]);
        console.log(table_id);
        
        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {

                    $(table_id).DataTable().ajax.reload();
                    
                    $(modal_id).modal('hide');
                    console.log("SaveModalForm Worked")
                }
                else {
                    $(modal_id +  ' .modal-content').html(data.html_form)
                }
            }

        })

        return false;

    };



    //Defining the Save Eligiblity Form variable
    var SaveEligibilityForm = function() {
        console.log("Save form function activted");
        $('.ajaxProgress').show()
        var form = $(this);
        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {
                    $('.ajaxProgress').hide();
                    $('#fm-modal-grid .modal-body').html(data.engagements);
                    //const newLocal = '#census_table tbody';
                    //$(newLocal).html(data.engagements1);
                    $('#census_table').DataTable().ajax.reload();
                    $('#modal-eligibility_rules').modal('hide');

                    
                    
                }
                else {
                    $('#modal-eligibility_rules .modal-content').html(data.html_form);
                }
            }

        })

        return false;
    };


    //Defining the Save Edit Form Variable
    var SaveEditForm = function () {

        var form = $(this);

        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {


                    $('#modal-edit_client').modal('hide');
                    
                    window.location.href = '/dashboard/client_page/' +data.slug
                
                }
                else{
                    $('#modal-edit_client .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    };

    //Defining the Save Edit Form Variable
    var SaveEditEngagementForm = function () {

    var form = $(this);
    console.log("Working")
    $.ajax({
        url: form.attr('data-url'),

        data: form.serialize(),

        type: form.attr('method'),

        dataType: 'json',

        success: function (data) {
            if (data.form_is_valid) {


                $('#modal-edit_engagement').modal('hide');
                
                window.location.href = '/dashboard/client_page/' +data.client_slug + '/engagement/' + data.engagement.slug
                console.log("Worked")
            }
            else{
                $('#modal-edit_engagement .modal-content').html(data.html_form)
            }
        }

    })

    return false;
};

    var SaveEditPrimaryUserForm = function () {

        var form = $(this);

        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {


                    $('#modal-edit_primary_client_user').modal('hide');
                    
                    window.location.href = '/dashboard/client_page/' +data.slug
                
                }
                else{
                    $('#modal-edit_primary_client_user .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    };


    

    // Create Client
    $(".show-client_form").click('#modal-new_client',ShowModalForm);
    $("#modal-new_client").on("submit", ".create-client_form",['#client_table','#modal-new_client'], SaveModalFormTable);


    //Edit Client
    $(".show-edit_client_form").click('#modal-edit_client',ShowModalForm);
    $('#modal-edit_client').on("submit",".edit-client_form",SaveEditForm);


    //Edit Primary Client User
    $(".show-edit_primary_client_user_form").click('#modal-edit_primary_client_user',ShowModalForm);
    $('#modal-edit_primary_client_user').on("submit",".edit-primary_client_user_form",SaveEditPrimaryUserForm);
    

    // Create Engagement
    $(".show-engagement_form").click("#modal-new_engagement", ShowModalForm);
    $("#modal-new_engagement").on("submit", ".create-form", ['#engagement_table','#modal-new_engagement'],SaveModalFormTable);


    //Edit Engagement
    $(".show-edit_engagement_form").click('#modal-edit_engagement',ShowModalForm);
    $('#modal-edit_engagement').on("submit",".edit-engagement_form",SaveEditEngagementForm);

    //Add Client Contact
    $(".show-add_contact_form").click('#modal-add_contact_form',ShowModalForm);
    $("#modal-add_contact_form").on("submit", ".add_contact_form",['#census_table','#modal-add_contact_form'], SaveModalFormTable);

    //Delete Client Contact
    $(".show-delete_contact_form").click('#modal-delete_contact',ShowModalForm);
    $("#modal-delete_contact").on("submit",".delete_contacts-form",['#census_table', '#modal-delete_contact'],SaveModalFormTable);
    
    // Edit Eligiblity
    $(".show-form").click('#modal-eligibility_rules',ShowModalForm);
    $("#modal-eligibility_rules").on("submit",".eligibility-form",SaveEligibilityForm);


    //Create Key Employees
    $(".show-key_employee-form").click("#modal-key_employee",ShowModalForm);
    $("#modal-key_employee").on("submit",".key_employee-form",['#census_table','#modal-key_employee'],SaveModalFormTable);


    //Make Selections
    $(".show-selections_form").click("#modal-selections",ShowModalForm);
    $("#modal-selections").on("submit",".selections-form",['#census_table','#modal-selections'],SaveModalFormTable);


    //Edit Selections
    $(".show-edit_selections_form").click("#modal-edit_selections",ShowModalForm);
    $("#modal-edit_selections").on("submit",".edit_selections_form",['#census_table','#modal-edit_selections'],SaveModalFormTable);


    //Show Census Statistics
    $(".show-census_statistics-form").click("#modal-census_statistics",ShowModalForm);

    //Show Engagement Profile
    $(".show-view_engagement_profile").click("#modal-view_engagement_profile",ShowModalForm);    

    //Show PY Selections
    $(".show-py_selections").click("#modal-py_selections",ShowModalForm)

    //Show Selections
    $(".view-selections_form").click("#modal-view_selections",ShowModalForm);

    //Show Upload Census Form
    $(".upload-census_form").click("#upload_census",ShowModalForm);


    //Update Census Table
    $('#census_list').on("click")

    //Show and Save Errors
    $(".show-view_errors").click("#modal-view_errors",ShowModalForm);
    $("#modal-view_errors").on("submit",".view_errors-form",['#census_table', '#modal-view_errors'],SaveModalFormTable);

    $("td").tooltip({container:'body'});



});

