$(document).ready(function () {
    $('#client_table').DataTable({
        "scrollY": "600px",
        "scrollCollapse": true,
        "paging": false,
    });
    $('.dataTables_length').addClass('bs-select');
});

