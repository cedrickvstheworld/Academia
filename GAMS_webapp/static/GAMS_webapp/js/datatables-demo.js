// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable();
});


$(document).ready(function() {
  $('#dataTable-salary').DataTable({
        "order": [ 1, "desc" ],
    } );
});

$(document).ready(function() {
  $('#dataTable-salary-all').DataTable({
        "order": [ 3, "desc" ],
    } );
});


    $(document).ready(function() {
        $('#dataTables-example').DataTable({
            responsive: true,
            "order": [ 0, "desc" ],
        });
    });

$(document).ready(function() {
        $('#dataTables-example2').DataTable({
            responsive: true,
            "order": [ 5, "desc" ],
        });
    });


$(document).ready(function() {
        $('#dataTables-example3').DataTable({
            responsive: true,
            "order": [ 0, "desc" ],
        });
    });


$(document).ready(function() {
        $('#dataTables-example4').DataTable({
            responsive: true,
            "order": [ 0, "desc" ],
        });
    });

