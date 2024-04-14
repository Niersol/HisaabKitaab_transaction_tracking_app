
---

# HisaabKitaab - Brand Transaction Management System

HisaabKitaab is a Django-based application designed to manage transactions between brand clients (parties) and users/staff. It was created according to the specific requirements of a client to facilitate efficient transaction tracking and management.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Features

### User Management

- **Custom User Model:** Inherits from `AbstractUser` with additional fields like `phone_number`, `question`, and `answer`.
- **Staff User:** Represents staff members with a one-to-one relationship to the custom `User` model.

### Party (Brand Client) Management

- **Party Model:** Represents brand clients associated with users.
- **Party Details:** Includes `name`, `phone_number`, and `address`.
- **Validation:** Ensures a party is not associated with a staff user or superuser.

### Transaction Management

- **Transaction Model:** Tracks transactions associated with parties.
- **Fields:** Includes `description`, `debit`, `credit`, and `time`.
- **Running Balance:** Calculates running balance based on previous transactions.

### Permissions and Security

- **User Permissions:** Defines custom permissions (`can_assign_staff`, `can_manage_transactions`) for user roles.
- **Data Protection:** Ensures compliance with data protection regulations.

## Usage

1. **User Authentication:** Users can register, login, and manage their profiles.
2. **Party Management:** Create, update, and delete brand clients (parties).
3. **Transaction Handling:** Add, edit, and view transactions for parties.
4. **Permissions:** Assign staff to users and manage transaction permissions.

## Client Requirements

This application was developed based on the specific requirements and objectives of a client to streamline brand-client transactions effectively.

## Contributing

Contributions are welcome! Please follow the [Contribution Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- Special thanks to the Django community for providing excellent resources and documentation.

---
