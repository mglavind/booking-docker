// filepath: /Users/mglavind/Documents/Projects/docker/booking-docker/bookingsystem/frontend/src/AktivitetsTeamBookingTable.js
import React, { useEffect, useState } from 'react';

const AktivitetsTeamBookingTable = () => {
    const [bookings, setBookings] = useState([]);

    useEffect(() => {
        fetch('/api/bookings/')
            .then(response => response.json())
            .then(data => setBookings(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    return (
        <div className="container mt-5">
            <h2>Aktivitets Team Bookings</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Team</th>
                        <th>Item</th>
                        <th>Team Contact</th>
                        <th>Status</th>
                        <th>Remarks</th>
                        <th>Start Date</th>
                        <th>Start Time</th>
                        <th>End Date</th>
                        <th>End Time</th>
                        <th>Created</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {bookings.map(booking => (
                        <tr key={booking.id}>
                            <td>{booking.id}</td>
                            <td>{booking.team}</td>
                            <td>{booking.item}</td>
                            <td>{booking.team_contact}</td>
                            <td>{booking.status}</td>
                            <td>{booking.remarks}</td>
                            <td>{booking.start_date}</td>
                            <td>{booking.start_time}</td>
                            <td>{booking.end_date}</td>
                            <td>{booking.end_time}</td>
                            <td>{booking.created}</td>
                            <td>{booking.last_updated}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AktivitetsTeamBookingTable;