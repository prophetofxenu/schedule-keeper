const errors = require('./errors');

// this looks like it does nothing, but leave it in case the offset comes back
function currentTime() {
    var dUTC = new Date();
    var milliseconds = dUTC.getTime();
    return new Date(milliseconds);
}

function isPM() {
    return currentTime().getHours() >= 12;
}

module.exports.dateDifference = function(date1, date2) {
    var millis = date2 - date1;
    if (date1 > date2)
        millis = date1 - date2;

    var hours = Math.floor(millis / 3600000);
    millis = millis - hours * 3600000;
    var minutes = Math.floor(millis / 60000);

    if (hours == 0) {
        return `${minutes} minutes`;
    } else {
        return `${hours} hours, ${minutes} minutes`;
    }
};

module.exports.humanReadableDate = function(date) {
    return date.toString().substring(0, 24);
};

module.exports.sqlDatetime = function(date) {
    return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ` +
           `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
};

module.exports.timeParameter = function(timeArg) {
    timeArg = timeArg.toLowerCase();

    var digits;
    var hour;
    var minute;
    //TODO refactor this
    if (/^(\d{1,2})([ap]m?)?$/i.test(timeArg)) {
        var match = /^(\d{1,2})([ap]m?)?$/i.exec(timeArg);
        hour = Number(match[1]);
        if (timeArg.includes('p') || (isPM() && !timeArg.includes('a'))) {
            hour += 12;
            if (hour == 24)
                hour = 12;
        }
        minute = 0;
    } else if (/^\d{3}([ap]m?)?$/i.test(timeArg)) {
        digits = timeArg.substring(0, 3);
        hour = Number(digits.substring(0, 1));
        if (timeArg.includes('p') || (isPM() && !timeArg.includes('a')))
            hour += 12;
        minute = Number(digits.substring(1));
    } else if (/^\d{4}([ap]m?)?$/i.test(timeArg)) {
        digits = timeArg.substring(0, 4);
        hour = Number(digits.substring(0, 2));
        if (timeArg.includes('p') || (isPM() && !timeArg.includes('a'))) {
            hour += 12;
            if (hour == 24)
                hour = 12;
        }
        minute = Number(digits.substring(2));
    } else if (/^\d:\d{2}([ap]m?)?$/i.test(timeArg)) {
        digits = timeArg.substring(0, 4);
        hour = Number(digits.substring(0, 1));
        if (timeArg.includes('p') || (isPM() && !timeArg.includes('a')))
            hour += 12;
        minute = Number(digits.substring(2));
    } else if (/^\d{2}:\d{2}([ap]m?)?$/i.test(timeArg)) {
        digits = timeArg.substring(0, 5);
        hour = Number(digits.substring(0, 2));
        if (timeArg.includes('p') || (isPM() && !timeArg.includes('a'))) {
            hour += 12;
            if (hour == 24)
                hour = 12;
        }
        minute = Number(digits.substring(3));
    } else {
        throw new errors.ValueError(`Invalid time ${timeArg}`);
    }

    if (hour === 12 && timeArg.includes('a'))
        hour = 0;

    if (hour > 23 || minute > 59) {
        throw new errors.ValueError(`Invalid time ${timeArg}`);
    }

    return {
        hour: hour,
        minute: minute
    };
};

module.exports.dateParameter = function(dateParam) {
    var match = /(\d{1,2})\/(\d{1,2})\/?(\d{2})?/.exec(dateParam);
    var month = parseInt(match[1]) - 1;
    var date = parseInt(match[2]);
    var year = match[3] != undefined ? parseInt('20' + match[3]) : undefined;
    
    if (month > 12 || date > 31) {
        throw new errors.ValueError(`Invalid time ${dateParam}`);
    }

    if (year == undefined) {
        year = new Date().getFullYear();
    }

    return new Date(year, month, date);
};

