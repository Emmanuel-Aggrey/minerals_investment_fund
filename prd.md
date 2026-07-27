MINERALS INCOME INVESTMENT FUND
Visitor Management System
Software Requirements Specification
Version 1.0 · May 2026
Field Details
Document Title MIIF Visitor Management System — Software Requirements Specification
Client Organisation Minerals Income Investment Fund (MIIF)
Physical Address No. 1 Rangoon Lane, Cannon House, Cantonments, Accra, Ghana
Data Controller solomon.dawson@miif.gov.gh
Document Version 1.0 (Initial Release)
Date May 2026
Status Draft for Developer Review

1. Introduction
   1.1 Project Overview
   The Minerals Income Investment Fund (MIIF) currently operates a standalone HTML-based visitor registration form at its premises at No. 1 Rangoon Lane, Cannon House, Cantonments, Accra. This document defines the full requirements for a web-based Visitor Management System (VMS) to replace and significantly extend that form into a multi-user, role-controlled platform.

The system shall support two user roles — Administrator and Front Office Officer — with clearly segregated permissions. Data handling must remain fully compliant with Ghana’s Data Protection Act, 2012 (Act 843) and the Presidential Moratorium of October 2025 on the use of NIA-based identity verification across public agencies.

1.2 Business Objectives
•Digitalise and centralise visitor check-in at MIIF premises.
•Enforce role-based access so that each Front Office Officer can only see records they have personally captured.
•Give Administrators full visibility, oversight, and reporting across all officers and all visits.
•Produce exportable reports in PDF and Excel for audit and compliance purposes.
•Automatically purge visitor records 30 days after the visit date to comply with Act 843.
•Maintain a complete audit trail of who registered each visitor and when.

1.3 Scope
The system shall be a responsive web application accessible from modern desktop browsers. The scope includes:
•User authentication and role management (Admin only).
•Visitor registration workflow (Front Office Officers).
•Visitor record management (search, view, update, check-out).
•Reporting and data export (PDF and Excel).
•Automated 30-day data purge with audit logging.
•System settings and configuration panel (Admin only).

Out of scope (for this version): mobile native applications, biometric or NIA API live integration, email/SMS notification to visitors.

1.4 Definitions and Abbreviations
Term / Abbreviation Meaning
MIIF Minerals Income Investment Fund
VMS Visitor Management System
Admin / Administrator Super-user role with full system access
Front Office Officer (FOO) Reception-level user who registers visitors
Act 843 Ghana Data Protection Act, 2012
NIA National Identification Authority (Ghana)
Ghana Card PIN National identity number in format GHA-XXXXXXXXX-X
PDF Portable Document Format
XLSX Microsoft Excel Open XML Spreadsheet format
SRS Software Requirements Specification (this document)
RBAC Role-Based Access Control

2. System Overview & Architecture
   2.1 User Roles
   The system shall implement exactly two user roles with the following high-level capabilities:

Capability Administrator Front Office Officer
Log in to the system Yes Yes
Register a new visitor Yes Yes
View own visitor records Yes Yes
View other officers’ visitor records Yes No
View all visitor records (full dashboard) Yes No
Export reports to PDF / Excel Yes (all records) Yes (own records only)
Create / edit / deactivate user accounts Yes No
Reset user passwords Yes No
Configure system settings Yes No
View system audit log Yes No
Manually delete visitor records Yes No

2.2 Technology Recommendations
The developer is free to choose the appropriate technology stack, however the following constraints must be respected:
•The application must run in a standard web browser with no client-side plugin installation required.
•All data must be stored in a relational database (e.g. PostgreSQL, MySQL, or equivalent).
•All communication between browser and server must use HTTPS.
•Passwords must be stored using a strong one-way hashing algorithm (e.g. bcrypt or Argon2).
•The application must be deployable on a standard Linux server or cloud hosting environment.

3. Functional Requirements
   3.1 Authentication & Session Management
   3.1.1 Login
   •The system shall provide a secure login page as the entry point for all users.
   •Users shall log in using a username (or email address) and password.
   •Failed login attempts shall display a generic error message (do not reveal whether the username or password was incorrect).
   •After 5 consecutive failed login attempts, the account shall be temporarily locked for 15 minutes. The Administrator shall be able to unlock accounts manually.
   •Sessions shall expire after 30 minutes of inactivity and require re-authentication.
   •A “Remember me” option may persist the session for up to 8 hours on trusted devices.

3.1.2 Password Management
•On first login, users created by an Administrator must be prompted to change their temporary password before accessing the system.
•Passwords must be at least 8 characters and include a mix of letters and numbers.
•An Administrator can reset any user’s password and send or display a temporary password.
•Users shall be able to change their own password from their profile settings.

3.1.3 Logout
•A visible Logout button must be accessible from all screens.
•On logout, the server session must be fully invalidated.

3.2 User Account Management (Administrator Only)
3.2.1 Create User Account
•The Administrator shall be able to create new Front Office Officer accounts.
•Required fields: Full Name, Username / Email, Role (fixed to ‘Front Office Officer’ at creation), Temporary Password, and Status (Active / Inactive).
•The Administrator may also create additional Administrator accounts.
•A confirmation prompt must be shown before saving a new account.

3.2.2 Edit User Account
•The Administrator shall be able to edit any user’s name, email, and status.
•Changing a user’s role must trigger a confirmation dialog.

3.2.3 Deactivate / Reactivate User Account
•The Administrator shall be able to deactivate an account without deleting it.
•A deactivated account must be immediately unable to log in.
•Visitor records created by a deactivated officer must remain in the system and be visible to the Administrator.
•The Administrator shall be able to reactivate a previously deactivated account.

3.2.4 User List View
•The Administrator shall see a list of all system users showing: Name, Username / Email, Role, Status (Active / Inactive), Date Created, Last Login.
•The list must be searchable and sortable.

3.3 Visitor Registration (Front Office Officer & Administrator)
The registration workflow is derived directly from the existing MIIF HTML form and is extended with additional fields and backend logic.

3.3.1 Privacy Notice Step
•Before the registration form is presented, the system must display the MIIF Privacy Notice as defined in the existing form (referencing the Data Protection Act, 2012 — Act 843).
•The user must acknowledge that the visitor has read and understood the notice by ticking a consent checkbox before proceeding.
•The privacy notice text must be editable by the Administrator in the system settings.

3.3.2 Visitor Personal Details (Step 1 of 3)
The following fields must be captured. Fields marked _ are mandatory.
Field Type Validation / Notes
Full Name _ Text Minimum 3 characters. Must match Ghana Card.
Phone Number _ Tel 7–20 digits. Accepts +, spaces, hyphens, brackets.
Email Address Email Optional. Must be valid format if provided.
Ghana Card PIN _ Text (split) Format: GHA-XXXXXXXXX-X. Middle part 9 chars, suffix 1 digit. Not stored permanently after verification.

•The Ghana Card PIN field must be displayed in three parts (prefix GHA-, 9-character middle segment, 1-digit suffix) consistent with the existing form.
•The PIN must be masked in the review step (displayed as GHA-•••••••••-•) and must NOT be stored in the database after the identity verification step is complete.

3.3.3 Visit Details (Step 2 of 3)
Field Type Validation / Notes
Person to Visit _ Text Full name of MIIF staff member being visited. Minimum 2 characters.
Department Dropdown Optional. Options: Executive Office, Finance & Accounts, Legal & Compliance, Investment & Portfolio, Operations, Human Resources, IT & Technology, Communications & PR, Internal Audit, Procurement, Other.
Purpose of Visit _ Chip select One of: Meeting, Official Business, Delivery, Interview, Contractor Work, Enquiry, Other.
Expected Duration Chip select Optional. Options: Under 30 min, 30–60 min, 1–2 hours, Half day, Full day.
Additional Notes Textarea Optional. Maximum 255 characters.

3.3.4 Review & Consent (Step 3 of 3)
•The system must display a read-only summary of all entered data for the visitor to verify before submission.
•The Ghana Card PIN must be shown masked at this stage.
•The visitor must tick a consent checkbox confirming they have read the MIIF Privacy Notice and consent to data processing.
•Submission must be blocked if consent is not given.

3.3.5 Submission & Reference Number
•On successful submission, the system must generate a unique reference number in the format MIIF-YYYYMMDD-XXXX (e.g. MIIF-20260517-7B3F).
•The entry time must be automatically recorded (server-side timestamp, not browser time).
•A data purge date of 30 days from the visit date must be calculated and stored.
•The system must record which Front Office Officer submitted the registration.
•A confirmation screen must display the reference number, visitor name, person being visited, purpose, entry time, and purge date.

3.3.6 Exit Time Recording
•When a visitor departs, the Front Office Officer must be able to locate the visitor’s record (by name or reference number) and record the exit time.
•The system must calculate and display the total duration of the visit.
•It must not be possible to record an exit time before the entry time.

3.4 Visitor Records & Search
3.4.1 Front Office Officer View
•A logged-in Front Office Officer shall only see visitor records that they personally registered.
•Records from other Front Office Officers must be completely hidden — not filtered, not blurred, but absent from all queries and views.
•The Officer shall be able to search and filter their own records by: visitor name, date range, purpose of visit, person visited, and department.

3.4.2 Administrator View
•The Administrator shall see all visitor records from all officers in a consolidated dashboard.
•The Administrator shall be able to filter records by: Front Office Officer, visitor name, date range, purpose, department, and visit status (pending / checked in / checked out).
•The Administrator shall be able to view the full detail of any individual visit record.

3.4.3 Record Detail View
Clicking a record must open a detail view showing all captured fields plus:
•Entry time and exit time (if recorded).
•Total visit duration.
•Registered by (officer name).
•Reference number.
•Data purge date.
•Consent status.

3.5 Reporting & Data Export
3.5.1 Report Scope Rules
•A Front Office Officer can generate reports containing only their own records.
•An Administrator can generate reports for all records, or filter by officer, date range, or any other available filter before exporting.
•These rules are enforced server-side and cannot be bypassed by URL manipulation.

3.5.2 PDF Report
•The PDF export must include the MIIF letterhead / logo, report title, report generation date and time, the filtering criteria applied, and the total number of records.
•Each record row must show: Reference No., Visitor Name, Phone, Person Visited, Department, Purpose, Entry Time, Exit Time, Duration, Registered By.
•The PDF must be generated server-side and delivered as a download.
•The Ghana Card PIN must never appear in any exported report.

3.5.3 Excel (XLSX) Report
•The Excel export must mirror the columns described for the PDF report.
•Column headers must be bold and the first row must be frozen.
•Auto-filter must be enabled on all columns.
•Date and time values must be formatted as readable text (not numeric serial dates).
•The Ghana Card PIN must never appear in any exported file.

3.6 Dashboard / Summary View
3.6.1 Front Office Officer Dashboard
•Total visits registered today (by this officer).
•Total visits this month (by this officer).
•Currently checked-in visitors (registered by this officer).
•Recent registrations table (last 10 records by this officer).

3.6.2 Administrator Dashboard
•Total visits today (all officers).
•Total visits this month (all officers).
•Active (checked-in) visitors right now.
•Breakdown of visits by purpose (chart or table).
•Breakdown of visits by department (chart or table).
•Most active Front Office Officer this month.
•Recent registrations table (last 20 records, all officers).

3.7 Automated Data Purge
•The system must automatically and permanently delete visitor records 30 days after the visit date, as required by Act 843.
•The purge must run as an automated background process (e.g. a scheduled task or cron job) at least once every 24 hours.
•Each purge event must be recorded in the system audit log: timestamp, number of records deleted, and any errors encountered.
•No manual action from any user should be required to trigger the routine purge.
•The Administrator may manually delete individual records before the 30-day period if required (e.g. data correction). This action must also be logged.

3.8 System Settings (Administrator Only)
•The Administrator must be able to edit the Privacy Notice text displayed on the registration form.
•The Administrator must be able to manage the list of departments available in the registration form.
•The Administrator must be able to manage the list of purposes of visit.
•The Administrator must be able to configure the session timeout duration.
•The Administrator must be able to view and export the system audit log.

4. Non-Functional Requirements
   4.1 Security
   •All pages must be served over HTTPS with a valid SSL/TLS certificate.
   •All user passwords must be hashed using bcrypt (cost factor ≥ 12) or Argon2id before storage.
   •The Ghana Card PIN must not be stored in the database beyond the point of identity verification. It must be cleared from all storage layers immediately after the check is complete.
   •Access control must be enforced on the server. A Front Office Officer must not be able to access another officer’s records by modifying a URL, API parameter, or HTTP request.
   •All form inputs must be sanitised to prevent SQL injection and cross-site scripting (XSS).
   •CSRF protection must be implemented on all state-changing forms.
   •Session tokens must be cryptographically random and invalidated on logout.
   •The system must implement HTTP security headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.

4.2 Performance
•Page load time (first meaningful paint) must not exceed 3 seconds on a standard broadband connection.
•Visitor registration form submission must return a response within 2 seconds under normal load.
•Report generation for up to 500 records must complete within 10 seconds.
•The system must support at least 10 concurrent users without degradation.

4.3 Usability
•The interface must be responsive and usable on desktop screens of 1280px width and above.
•Error messages must be clear, human-readable, and displayed adjacent to the field that caused them.
•All mandatory fields must be visually distinguished (e.g. red dot or asterisk indicator consistent with the existing form design).
•The registration form must preserve the multi-step (wizard) layout of the existing HTML form: Privacy → Personal Details → Visit Details → Review & Consent.
•A progress bar or step indicator must be shown during registration.

4.4 Reliability & Availability
•The system must target 99% uptime during business hours (Monday–Friday, 07:00–18:00 GMT).
•The system must perform daily automated database backups. Backups must be retained for a minimum of 7 days.
•The application must handle database connection failures gracefully and display a user-friendly error message rather than exposing stack traces.

4.5 Data Protection & Compliance
•All data handling must comply with the Data Protection Act, 2012 (Act 843) of Ghana.
•Visitor data must not be shared with or transmitted to third parties except where explicitly required by law.
•The 30-day automated purge is a legal requirement and must be implemented as a core feature, not an optional add-on.
•The system must provide the Data Controller (solomon.dawson@miif.gov.gh) with the ability to respond to data subject access requests by searching for records by visitor name or reference number.

5. Data Model (Reference)
   The following tables describe the minimum data entities the system must store. The developer may normalise or extend these as needed.

5.1 Users Table
Field Type Notes
id Integer (PK) Auto-increment primary key
full_name VARCHAR(120) Officer’s full name
username VARCHAR(100) Unique. Used for login.
email VARCHAR(180) Unique. Optional alternative login identifier.
password_hash VARCHAR(255) bcrypt or Argon2id hash
role ENUM ‘admin’ or ‘front_officer’
status ENUM ‘active’ or ‘inactive’
must_change_password BOOLEAN True on first login
created_at TIMESTAMP Account creation date
last_login_at TIMESTAMP Last successful login

5.2 Visitors Table
Field Type Notes
id Integer (PK) Auto-increment primary key
reference_number VARCHAR(30) Unique. Format: MIIF-YYYYMMDD-XXXX
full_name VARCHAR(120) Visitor’s full name
phone VARCHAR(25) Visitor phone number
email VARCHAR(180) Optional visitor email
ghana_card_pin VARCHAR(20) Cleared to NULL after verification. Never exported.
person_to_visit VARCHAR(120) Name of MIIF staff member
department VARCHAR(80) Optional department
purpose VARCHAR(60) Purpose of visit
expected_duration VARCHAR(30) Optional duration selection
notes TEXT Optional additional notes (max 255 chars)
consent_given BOOLEAN True if visitor consented
entry_time TIMESTAMP Server-side timestamp on form submission
exit_time TIMESTAMP Recorded by officer on departure. Nullable.
visit_date DATE Date portion of entry_time
purge_date DATE visit_date + 30 days
registered_by Integer (FK) Foreign key to Users.id
created_at TIMESTAMP Record creation timestamp

5.3 Audit Log Table
Field Type Notes
id Integer (PK) Auto-increment primary key
actor_id Integer (FK) User who performed the action
action VARCHAR(80) e.g. ‘visitor_registered’, ‘record_deleted’, ‘user_created’
target_type VARCHAR(40) e.g. ‘visitor’, ‘user’
target_id Integer ID of the affected record
detail TEXT JSON or human-readable description of the change
ip_address VARCHAR(45) IP address of the actor
created_at TIMESTAMP When the action occurred

6. Required Screens & Modules
   Screen / Module Accessible By Description
   Login Page All Username/password authentication
   Change Password (first login) All Mandatory on first login for new accounts
   Dashboard All (role-filtered content) Summary statistics and recent records
   New Visitor Registration All Multi-step wizard: Privacy → Identity → Visit → Review
   Registration Confirmation All Success screen with reference number
   My Visitors (list + search) Front Office Officer Own records only, with filters and export
   All Visitors (list + search) Administrator All records across all officers, with filters and export
   Visitor Detail View All (own records / Admin: any) Full detail of a single visit record
   Record Exit Time All (own records / Admin: any) Mark visitor as departed and log exit time
   User Management — List Administrator List of all system user accounts
   User Management — Create/Edit Administrator Form to create or edit a user account
   System Settings Administrator Edit privacy notice text, departments, purposes, session timeout
   Audit Log Administrator Searchable log of all system events
   Reports / Export All (role-filtered) Generate and download PDF or Excel reports
   Profile / Change Password All User’s own profile and password change
   Logout All Session termination

7. Visitor Registration Form — Detailed Specification
   This section documents the exact field behaviours required, derived from the existing MIIF HTML registration form that the developer should use as the baseline UI reference.

7.1 Form Validation Rules
Field Rule
Full Name Required. Minimum 3 characters. Error shown on blur if invalid.
Phone Number Required. Regex: 7–20 characters, digits plus +, spaces, -, (, ) allowed.
Email Address Optional. If filled, must match standard email regex. Error on blur.
Ghana Card PIN — Middle Required. Exactly 9 alphanumeric characters. Auto-advances cursor to suffix field on completion.
Ghana Card PIN — Suffix Required. Exactly 1 digit.
Person to Visit Required. Minimum 2 characters.
Purpose of Visit Required. Must select one chip option. Error shown on Next if not selected.
Department Optional. Dropdown with predefined options.
Expected Duration Optional. Chip selection.
Additional Notes Optional. Maximum 255 characters. Character counter displayed.
Consent Checkbox Required. Submission blocked and error shown if not ticked.

7.2 Field-Level Error Behaviour
•Validation errors must appear immediately below the offending field.
•A summary error banner must also appear at the top of the current step when the user attempts to proceed.
•Errors must clear in real-time as the user corrects the field (on input event, not only on blur).

7.3 Step Navigation
•The user may navigate back to any previous step without losing entered data.
•Forward navigation to the next step is blocked until all required fields on the current step pass validation.
•A progress bar must reflect the current step visually (0%, 33%, 66%, 95%, 100% on completion).

8. Branding & Design Guidelines
   The web application must be consistent with the MIIF brand identity established in the existing registration form. The developer should treat the existing HTML file as the primary design reference for the visitor-facing registration screens.

8.1 Colour Palette
Colour Hex Value Usage
Gold #C9A84C Primary accent, progress bar, chip selected state, CTA buttons
Gold Light #EDD98A Hover states on gold elements
Gold Dark #8B6914 Text on gold backgrounds, notice headers
Ink (Dark) #1A1A1A Primary background (header/footer), primary text
Surface #F6F4EF Page background
White #FFFFFF Card / form field backgrounds
Error Red #C0392B Validation error messages and borders
Success Green #1A7A4A Success banners and purge date colour

8.2 Typography
•Primary font: DM Sans (Google Fonts) for all body text and UI elements.
•Display / heading font: DM Serif Display (Google Fonts) for screen titles and the confirmation heading.
•Base font size: 16px. Body text: 13–15px. Labels and hints: 10–12px.

8.3 UI Component Requirements
•Multi-step registration must use the existing step wizard pattern (chip label + screen title + description + fields + navigation buttons).
•Purpose of visit and Expected Duration selections must use the chip / pill button pattern (not a standard dropdown).
•Primary call-to-action buttons must use the full-width, rounded button style from the existing form.
•The gold-coloured Continue button must be used for the initial Privacy step; dark buttons for subsequent steps.
•Form fields must show a gold focus ring on active state.
•The administration dashboard may adopt a different (more information-dense) layout appropriate to a back-office tool, while retaining the brand colours and fonts.

9. Deliverables & Acceptance Criteria
   9.1 Expected Deliverables
   1.Fully functional web application deployed to a staging / test URL for client review.
   2.Source code delivered in a version-controlled repository (GitHub, GitLab, or equivalent).
   3.Database schema (SQL migration scripts or ORM migrations).
   4.Deployment documentation: instructions for deploying the application to a production Linux server.
   5.A basic system administration guide covering: creating the first Admin user, backups, and the purge schedule.
   6.A user guide covering: Admin user management, visitor registration, reporting, and export.

9.2 Acceptance Criteria
The following conditions must all be satisfied before final delivery is accepted:
•A Front Office Officer can register a visitor through the complete multi-step form.
•A reference number is generated and displayed on the confirmation screen.
•A Front Office Officer cannot view, search, or export records belonging to any other officer.
•The Administrator can view all records from all officers on a single dashboard.
•Reports can be exported as both PDF and Excel, with the correct data scope per role.
•The Ghana Card PIN does not appear in any database record (after verification), exported file, or report.
•An Administrator can create, edit, deactivate, and reactivate a Front Office Officer account.
•The automated 30-day purge is demonstrably functional (developer must provide test evidence).
•All security requirements in Section 4.1 are verifiably implemented.
•The application passes basic accessibility checks (readable without CSS, keyboard-navigable login and registration).

10. Assumptions & Open Questions
    10.1 Assumptions
    •MIIF will provide the developer with the official logo file (PNG or SVG) for use in the application header and PDF reports.
    •The application will be hosted on a server or cloud environment procured and managed by MIIF or its IT team.
    •NIA identity verification will remain a manual process (front office officer checks the physical Ghana Card against the submitted PIN). Live API integration with NIA is out of scope.
    •The initial Administrator account will be seeded by the developer during deployment; subsequent admin accounts can be created in-system.
    •MIIF will provide the developer with any departmental or organisational updates to the department list before go-live.

10.2 Open Questions for the Developer
•What hosting environment (shared hosting, VPS, cloud PaaS) are you proposing, and what are the cost implications?
•What technology stack (language, framework, database) do you recommend, and why?
•How will you handle the daily purge job in the proposed environment (cron, scheduler service, etc.)?
•What is your proposed approach to HTTPS certificate management?
•Will you provide an SLA for bug fixes during a warranty period post-delivery?

11. Appendix — Reference Document
    The existing MIIF Visitor Registration Form (HTML file: MIIF_Visitor_Registration_Form_1.html) is provided as an attachment to this SRS. The developer must treat this file as the canonical UI reference for:
    •The multi-step registration wizard flow (screens 0–4).
    •All field names, validation rules, and error messages.
    •The visual design language (colours, typography, spacing, component styles).
    •The privacy notice text and Data Protection Act compliance wording.
    •The post-submission confirmation screen content and layout.

Deviations from the UI reference in the visitor-facing registration screens must be discussed and approved by MIIF before implementation.

End of Document
Minerals Income Investment Fund · Confidential
