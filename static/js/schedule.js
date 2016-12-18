
var button = $('#activate');
button.click(function() {
    button.attr('disabled', 'disabled');
    $.post("/activate");
    setTimeout(function() {
        button.removeAttr('disabled');
    }, 7000);
});

function neededRows(parsedSchedule) {
    var largest = 0;
    for(var key in parsedSchedule) {
        var ary = parsedSchedule[key];
        if(ary.length > largest) {
            largest = ary.length;
        }
    }
    return largest;
}

function toFriendlyTime(hour, minute) {
    var amPm = 'AM';
    if(hour === 0) {
        hour = 12;
    } else if(hour > 12) {
        amPm = 'PM';
        hour = hour - 12;
    }
    var hourStr = hour.toString();
    if (hourStr.length === 1) hourStr = '0' + hourStr;
    var minuteStr = minute.toString();
    if (minuteStr.length === 1) minuteStr = '0' + minuteStr;
    return hourStr + ':' + minuteStr + ' ' + amPm;
}

function displaySchedule(schedule) {
    var parsedSchedule = {
        0: [],
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
    };

    for (var i = 0; i < schedule.length; i++) {
        var recur = schedule[i];
        var day_id = recur.day_id;
        recur.day_id = undefined;
        parsedSchedule[day_id].push(recur);
    }

    var rows = neededRows(parsedSchedule);
    for(var i = 0; i < rows; i++) {
        $('<tr><td dayid="6"/><td dayid="0"/><td dayid="1"/><td dayid="2"/><td dayid="3"/><td dayid="4"/><td dayid="5"/></tr>').insertBefore('tbody #add-recurrence-row');
    }

    for(var key in parsedSchedule) {
        var recur = parsedSchedule[key];
        for(var rowIndex = 0; rowIndex < recur.length; rowIndex++) {
            var targetColumn = $('tbody tr:nth-child(' + (rowIndex + 1) + ') td[dayid=' + key + ']');
            if (targetColumn) {
                targetColumn.append('<span>' + toFriendlyTime(recur[rowIndex].hour, recur[rowIndex].minute) + "</span>");
            }
        }
    }
}

function refresh() {
    $('#countdown').text('Loading...');
    $('tbody tr[id!=add-recurrence-row]').remove();
    get('/schedule', function(response, err) {
        var countdown = $('#countdown');
        if(response.next_occurrence === -1) {
            countdown.text('No recurrence schedule has been set yet!');
        } else {
            var mom = moment(response.next_occurrence);
            countdown.html('<b>Next recurrence:</b> ' + mom.format("h:mm A on dddd MMMM D, YYYY") + ' <i>(' + mom.fromNow() + ')</i>');
        }
        displaySchedule(response.schedule);
    });
}

$('#refresh').click(function() {
    refresh();
});

$(document).ready(function() {
    refresh();
});

$('.add-recurrence').timepicker({
    step: 15,
    wrapHours: true
});

$('.add-recurrence').on('changeTime', function() {
    var date = $(this).timepicker('getTime');
    var data = {
        day_id: parseInt($(this).attr('dayid')),
        hour: date.getHours(),
        minute: date.getMinutes()
    };
    post('/add_occurrence', data, function(response, error) {
        if(error) {
            alert(error);
            return;
        }
        refresh();
    });
});

$('.add-recurrence').click(function(e) {
    e.preventDefault();
    $(this).timepicker('show');
});