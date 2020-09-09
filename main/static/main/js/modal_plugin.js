$(document).ready(function () {
    //Defining the Show Engagement Form Variable

    var ShowEngagementForm = function () {
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
    };

    //Defining the Save Engagement Form Variable
    var SaveEngagementForm = function () {

        var form = $(this);
        
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
    };

    //Defining the Show Form Variable
    var ShowForm = function () {
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

    //Defining the Show Edit Client Form variable
    var ShowEditClientForm = function () {
        console.log("ShowForm Activated");
        var btn = $(this);

        $.ajax({
            url: btn.attr("data-url"),

            type: 'get',

            dataType: 'json',

            beforeSend: function () {
                $('#modal-edit_client').modal('show');
            },

            success: function (data) {
                $('#modal-edit_client .modal-content').html(data.html_form);
            }
        });
    };

    //Defining the Show Eligiblity Form
    var ShowEligiblityForm = function (){
        console.log("Eligiblity Form Activated");
        $('.ajaxProgress').show();
        var btn=$(this);

        $.ajax({

            url: btn.attr("data-url"),

            type: 'get',

            dataType: 'json',

            beforeSend: function (){
                $('#modal-eligibility_rules').modal('show');
            },
            success: function (data){
                $('.ajaxProgress').hide();
                $('#modal-eligibility_rules .modal-content').html(data.html_form);
            }

        })
    }

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

    //Defining the Show Census Form Variable
    var ShowCensusForm = function (){
        console.log("Census Form Working")
        var btn = $(this);

        $.ajax({

            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend:function(){
                $("#upload_census").modal("show");
            },

            success: function(data){
                $("#upload_census .modal-content").html(data.html_form)
            }
            
        })
    };

    //Defining the Show Key Employee Form Variable
    var KeyEmployeeForm = function (){
        $('.ajaxProgress').show()
        var btn = $(this);

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-key_employee").modal("show");
            },

            success: function (data){
                $('.ajaxProgress').hide();
                $("#modal-key_employee .modal-content").html(data.html_form);
            }
        })
    };

    //Defining the Save Key Employee Form variable
    var SaveKeyEmployeeForm = function() {
        $('.ajaxProgress').show()
        var form = $(this);
        $.ajax({

            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {
                    $('.ajaxProgress').hide()
                    //$('#census_table tbody').html(data.engagements)
                    $('#census_table').DataTable().ajax.reload();
                    $('#modal-key_employee').modal('hide');
                    console.log('Key Employee Form Saved');
                    console.log(data.engagements)
                }
                else {
                    $('#modal-key_employee .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    };

    //Defning the Show Make Selection Form variable
    var ShowMakeSelectionsForm = function (){

        var btn = $(this);

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-selections").modal("show");
            },

            success: function (data){
                $("#modal-selections .modal-content").html(data.html_form);
            }
        })
    };

    //Defining the Save Selection Form
    var SaveSelections = function() {
        var form = $(this);
        $.ajax({

            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {
                    $('#census_table').DataTable().ajax.reload();

                    $('#modal-selections').modal('hide');
                    console.log("Save Selections worked");
                }
                else {
                    $('#modal-selections .modal-content').html(data.html_form)
                }
            }

        })

        return false;
    };

    //Defining the Census Statistics variable
    var CensusStatistics = function (){
        console.log("Census Statistics");
        var btn = $(this);

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-census_statistics").modal("show");
            },

            success: function (data){
                $("#modal-census_statistics .modal-content").html(data.html_form);
            }
        })
    };

    //Defining the Census Statistics variable
    var ShowPreviousSeletions = function (){
        console.log("PY Selections");
        var btn = $(this);

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-py_selections").modal("show");
            },

            success: function (data){
                $("#modal-py_selections .modal-content").html(data.html_form);
            }
        })
    };    

    //Defining the View Selection form variable
    var ViewSelections = function (){
        var btn = $(this);

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-view_selections").modal("show");
            },

            success: function (data){
                $("#modal-view_selections .modal-content").html(data.html_form);
            }
        })
    };
    
    //Defining the Show Delete Form Variable
    var ShowDeleteForm = function () {
        var btn=$(this);

        $.ajax({

            url: btn.attr("data-url"),

            type:'get',

            dataType:'json',

            beforeSend: function (){
                $('#modal-delete_client').modal('show');
            },

            success: function (data) {
                $('#modal-delete_client .modal-content').html(data.html_form);

            }

        });
    };

    //Defining the Save Delete Form variable
    var SaveDeleteForm = function () {
        var form =$(this);

        $.ajax({
            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType:'json',

            success: function (data){
                $('#modal-delete_client').modal('hide');
            }
        });
        $('#modal-delete_client').modal('hide');
        return false;
    };


    //Defining the save form variable
    var SaveForm = function () {
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
                
                }
                else{
                    $('#modal-new_client .modal-content').html(data.html_form)
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

    var ViewErrors = function (){
        var btn = $(this);
        console.log("Working");

        $.ajax({
            
            url:btn.attr("data-url"),

            type:'get',

            dataType:"json",

            beforeSend: function (){
                $("#modal-view_errors").modal("show");
            },

            success: function (data){
                $("#modal-view_errors .modal-content").html(data.html_form);
                console.log("Worked");
            }
        })
    };

    //Defining the Save Key Employee Form variable
    var SaveErrorsForm = function() {
        $('.ajaxProgress').show()
        var form = $(this);
        console.log("Save Error Form Running")
        $.ajax({

            url: form.attr('data-url'),

            data: form.serialize(),

            type: form.attr('method'),

            dataType: 'json',

            success: function (data) {
                if (data.form_is_valid) {
                    $('.ajaxProgress').hide();
                
                    
                    $('#census_table').DataTable().ajax.reload();

                    $('#modal-view_errors').modal('hide');
                }
                else {
                    $('#modal-view_errors.modal-content').html(data.html_form)
                }
            }

        })

        return false;
    };

    

    // Create Client
    $(".show-client_form").click(ShowForm);
    
    $("#modal-new_client").on("submit", ".create-client_form", SaveForm);

    //Edit Client
    $(".show-edit_client_form").click(ShowEditClientForm);
    
    $('#modal-edit_client').on("submit",".edit-client_form",SaveEditForm);
    

    // Edit Eligiblity
    $(".show-form").click(ShowEligiblityForm);
    $("#modal-eligibility_rules").on("submit",".eligibility-form",SaveEligibilityForm);


    // Create Engagement
    $(".show-engagement_form").click(ShowEngagementForm);
    $("#modal-new_engagement").on("submit", ".create-form", SaveEngagementForm);

    //Create Key Employees
    $(".show-key_employee-form").click(KeyEmployeeForm);
    $("#modal-key_employee").on("submit",".key_employee-form",SaveKeyEmployeeForm);

    $(".show-selections_form").click(ShowMakeSelectionsForm);
    $("#modal-selections").on("submit",".selections-form",SaveSelections);


    //Show Census Statistics
    $(".show-census_statistics-form").click(CensusStatistics);

    //Show PY Selections
    $(".show-py_selections").click(ShowPreviousSeletions)

    //Show Selections
    $(".view-selections_form").click(ViewSelections);

    //Show Upload Census Form
    $(".upload-census_form").click(ShowCensusForm);

    
    //Update Client List
    $('#client_list').on("click", ".show-form-update", ShowForm);
    $("#modal-new_client").on("submit", ".update-form", SaveForm);
    

    //Update Engagement List
    $('#engagement_list').on("click", ".show-form-update", ShowEngagementForm)
    $("#modal-new_engagement").on("submit", ".update-form", SaveEngagementForm);

    //Update Census Table
    $('#census_list').on("click")

    //Delete Engagement
    $(".show-delete-form").click(ShowDeleteForm);
    $("#modal-delete_client").on("submit",".delete-form", SaveDeleteForm);

    //Show Errors
    $(".show-view_errors").click(ViewErrors);

    $("#modal-view_errors").on("submit",".view_errors-form",SaveErrorsForm);

    $("td").tooltip({container:'body'});



});

