// filepath: /Users/mglavind/Documents/Projects/docker/booking-docker/bookingsystem/frontend/src/BookingScheduler.js
import React, { useEffect, useRef, useState } from 'react';
import Gantt from 'frappe-gantt';

function BookingScheduler() {
    const ganttRef = useRef(null);
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        fetch('/api/bookings/')
            .then(response => response.json())
            .then(data => {
                const formattedTasks = data.map(booking => ({
                    id: booking.id,
                    name: booking.name || `Booking ${booking.id}`,
                    start: `${booking.start_date} ${booking.start_time}`,
                    end: `${booking.end_date} ${booking.end_time}`,
                    progress: 100, // Assuming all tasks are completed for simplicity
                    dependencies: '', // Assuming no dependencies for simplicity
                }));
                setTasks(formattedTasks);
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    useEffect(() => {
        if (ganttRef.current && tasks.length > 0) {
            new Gantt(ganttRef.current, tasks, {
                view_mode: 'Hour',
                view_mode_select: true,
                on_click: (task) => {
                    console.log(task);
                },
                on_date_change: (task, start, end) => {
                    console.log(task, start, end);
                },
                on_progress_change: (task, progress) => {
                    console.log(task, progress);
                },
                on_view_change: (mode) => {
                    console.log(mode);
                },
            });
        }
    }, [tasks]);

    return (
        <div className='booking-scheduler'>
            <header className='BookingScheduler-header'>
                <h1>Booking Scheduler</h1>
            </header>
            <div ref={ganttRef}></div>
        </div>
    );
}

export default BookingScheduler;