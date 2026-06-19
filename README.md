# 🏥 Queue Cure '26

## Introduction

I built Queue Cure for the Queue Cure '26 Hackathon.
The idea came from a common problem seen in many clinics. Patients usually take a token and wait without knowing when their turn will come. Receptionists also have to manage the queue manually, which can create confusion.
To make this process easier, I developed a real-time queue management system where both the receptionist and patients can track the queue digitally.

---

## What My Project Does

The project has two screens:

### 1. Receptionist Screen

The receptionist can:

* Add new patients
* Generate tokens automatically
* Delete patients
* Set average consultation time
* Call the next patient
* Handle emergency patients with higher priority

### 2. Patient Screen

Patients can see:

* Current token being served
* Current patient name
* Number of patients ahead
* Estimated waiting time
* Queue progress
* Doctor availability status

---

## Real-Time Functionality

One of the main goals of this project was to avoid manual page refreshes.

I used Flask-SocketIO so that whenever the receptionist clicks "Call Next", the patient screen updates automatically in real time.

---

## Technologies Used

* Python
* Flask
* SQLite
* Flask-SocketIO
* HTML
* CSS
* JavaScript

---

## Features Added Beyond Basic Requirements

* Emergency patient priority
* Duplicate patient checking
* Current patient tracking
* Queue progress percentage
* Dynamic waiting time calculation
* Queue reset option for testing

---

## Challenges I Faced

The most challenging part was implementing real-time synchronization between both screens.
Initially, the patient page was not updating automatically. After learning and implementing Flask-SocketIO correctly, I was able to synchronize both screens successfully.
Another challenge was handling emergency patients while maintaining proper queue order.

## Future Improvements

If I continue working on this project, I would like to add:

* SMS notifications
* WhatsApp alerts
* Online appointment booking
* Multi-doctor support
* Doctor dashboard
---

## Final Thoughts

This project helped me understand Flask, databases, real-time communication using Socket.IO, and how technology can improve patient experience in clinics.
Queue Cure is a simple but practical solution that can make clinic queue management more organized and transparent.
