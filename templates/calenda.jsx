
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        selectable: true,
        initialView: 'dayGridMonth',
        themeSystem: 'bootstrap',
        editable: true,
        events: [
            {% for data in processed_data %}
            {
                title: '{{ data.title }}',
                start: '{{ data.production_date }}',
                end: '{{ data.closing_date }}',
                className: 'bg-blue',
                dragabble: true
            },
            {% endfor %}
        ]
    });

    calendar.render();
