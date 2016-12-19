$('.datepicker').pickadate({
    selectMonths: true,
    selectYears: 15,
    container: 'body'
});

$('.timepicker').pickatime({
    autoclose: false,
    twelvehour: true,
    container: 'body'
});

$('#modal-submit').click(function() {
    var date = $('#date').val();
    var time = $('#time').val();
    var dateTime = moment(date + ' ' + time).toDate();

    var data = {
        year: dateTime.getFullYear(),
        month: dateTime.getMonth() + 1,
        day: dateTime.getDate(),
        hour: dateTime.getHours(),
        minute: dateTime.getMinutes()
    };

    var btn = $(this);
    btn.attr('disabled', 'disabled');
    post('/add_onetime_occurrence', data, function(response, error) {
        if (error) {
            btn.removeAttr('disabled');
            alert(error);
            return;
        }
        refresh();
    });
});