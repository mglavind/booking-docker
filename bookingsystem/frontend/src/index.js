import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import AktivitetsTeamBookingTable from './AktivitetsTeamBookingTable';
import BookingScheduler from './BookingScheduler';


const appDiv = document.getElementById('app');
const aktivitetsTeamBookingTableDiv = document.getElementById('aktivitets-team-booking-table');
const bookingSchedulerDiv = document.getElementById('booking-sheduler');

if (appDiv) {
    ReactDOM.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>,
        appDiv
    );
}

if (aktivitetsTeamBookingTableDiv) {
    ReactDOM.render(
        <React.StrictMode>
            <AktivitetsTeamBookingTable />
        </React.StrictMode>,
        aktivitetsTeamBookingTableDiv
    );
}

if (bookingSchedulerDiv) {
    ReactDOM.render(
        <React.StrictMode>
            <BookingScheduler />
        </React.StrictMode>,
        bookingSchedulerDiv
    );
}

if (module.hot) {
    module.hot.accept();
}