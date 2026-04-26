# Flight Skeleton Project Instructions

This document provides guidelines and best practices for structuring and developing a project using the Flight PHP framework.

## Instructions for AI Coding Assistants

As you are developing this project, follow these guidelines as close as you can. If you are unsure about something, ask for clarification before proceeding. You should feel 95% confident in the coding decisions that you make, but allow yourself an offramp if you are not sure about something to ask questions.

## Project Structure

Organize your project as follows:

project-root/
│
├── app/                # Application-specific code
│   ├── commands/       # Custom CLI commands for Runway (built using adhocore/cli)
│   ├── config/         # Configuration files (database, app settings, routes)
│                       # Key files in this folder:
│                       #   - bootstrap.php: Bootstraps and connects the files in the config folder.
│                       #   - routes.php: Route definitions.
│                       #   - services.php: Service definitions (where config variables are used and injected).
│   ├── controllers/    # Route controllers (e.g., HomeController.php)
│   ├── logic/          # (For large projects) Business logic classes/services, called from controllers
│   ├── middlewares/    # Custom middleware classes/functions
│   ├── models/         # Data models (if needed, usually using flightphp/active-record)
│   ├── utils/          # Utility/helper functions
│   └── views/          # View templates (if using)
│
├── public/             # Web root (index.php, assets, etc.)
│
├── vendor/             # Composer dependencies
│
├── tests/              # Unit and integration tests
│
├── composer.json       # Composer config
│
└── README.md           # Project overview

## Development Guidelines

- **Controllers:** Place all route-handling logic in `app/controllers/`. Each controller should handle a specific resource or feature. For large projects, move business logic out of controllers and into the `app/logic/` directory as dedicated classes/services, and call them from your controllers. Use appropriate namespaces for organization. By default, all controllers inject the `Engine $app` variable unless this project has its own dependency injection handler.
- **Namespaces:** Use lowercase namespaces for all classes in the `app/` directory. For example, `app/controllers/HomeController.php` should have the namespace `app\controllers`.
- **Middlewares:** Store reusable middleware in `app/middlewares/`. Register them in your bootstrap or route files.
- **Utils:** Place helper functions and utilities in `app/utils/`.
- **Models:** If your app uses data models, keep them in `app/models/`.
- **Views:** Store templates in `app/views/` if using a templating engine.
- **Config:** Use the `app/config/` directory for configuration files. The main config file is `config.php`, which should be created by copying `config_sample.php` and updating as needed. In other main bootstrap files like bootstrap, and services.php, the $config variable is available to use to access configuration values.
- **Public:** Only expose the `public/` directory to the web server. All requests should go through `public/index.php`.
- **Environment:** Do not use .env files; all configuration should be managed in `app/config/config.php`.
- **Routes:** Define routes in `app/config/routes.php`. Use the `$router->map()` method to register routes with all request methods or `$router->get()` for `GET $router->post()` for POST etc. and associate them with controller methods. Best practice for defining the controller is [ MyController::class, 'myMethod' ].

## Mandatory Validation Checklist

After successfully implementing a change, you MUST run the following commands to validate your work. Address any errors before concluding the task.

1.  **Run Linter:**
    ```bash
    composer lint
    ```
2.  **Run Code Style Check:**
    ```bash
    composer phpcs
    ```
3.  **Run Tests:**
    ```bash
    composer test
    ```

## Getting Started

1. Clone the repository and run `composer install`.
2. Copy `app/config/config_sample.php` to `app/config/config.php` and update configuration values as needed.
3. Set your web server's document root to the `public/` directory.
4. Add new controllers, middlewares, and utilities as needed, following the structure above.
5. Register routes and middlewares in your bootstrap file (usually `public/index.php`).

## CLI Commands

Flight projects can include custom CLI commands to automate tasks such as migrations, seeding, or maintenance. The recommended CLI tool is [flightphp/runway](https://github.com/flightphp/runway), which builds on the [adhocore/cli](https://github.com/adhocore/cli) package (not Symfony Console).

- Place your custom command classes in the `app/commands/` directory.
- Runway will automatically discover and register commands from this directory.
- All CLI commands should be built using the adhocore/cli package (do not use Symfony Console).
- Use CLI commands to manage your application, generate code, or perform routine tasks.

Refer to the Runway documentation for details on creating and using custom commands with adhocore/cli.

## Additional Tips

- Keep controllers focused and small; delegate global or common logic to `app/utils/` when possible. For large projects, move business logic to `app/logic/` and use appropriate namespaces.
- Write tests for class files in the `tests/` directory.
- Use Composer for dependency management.
- Document your code and update the README as your project evolves.
- **Favor simplicity and minimalism:** Keep your codebase simple and avoid unnecessary abstractions or complexity. Only add dependencies when absolutely necessary, as fewer dependencies mean fewer potential issues and security risks.
- **Follow coding standards:** Use PSR1 coding standards and strict comparisons (`===`). Maintain a high level of code quality and consistency throughout your project.
- **Test thoroughly:** Regularly run and maintain tests for your codebase. Ensure your application works as expected.

For more details, see the README file or visit the Flight documentation.

## Suggested Packages

Flight is highly extensible. Here are some recommended packages and plugins for common needs:

- **ORM / Database:**
  - [flightphp/core](https://github.com/flightphp/core) PdoWrapper (simple PDO wrapper)
  - [flightphp/active-record](https://github.com/flightphp/active-record) (official ORM/Mapper)
  - [byjg/php-migration](https://github.com/byjg/php-migration) (database migrations)
- **Session:**
  - [flightphp/session](https://github.com/flightphp/session) (official session library)
  - [Ghostff/Session](https://github.com/Ghostff/Session) (advanced session manager)
- **Permissions:**
  - [flightphp/permissions](https://github.com/flightphp/permissions) (official permissions library)
- **Caching:**
  - [flightphp/cache](https://github.com/flightphp/cache) (official in-file caching)
- **CLI:**
  - [flightphp/runway](https://github.com/flightphp/runway) (official CLI tool, built on adhocore/cli)
- **Cookies:**
  - [overclokk/cookie](https://github.com/overclokk/cookie) (cookie management)
- **Debugging:**
  - [tracy/tracy](https://github.com/nette/tracy) (error handler and debugger)
  - [flightphp/tracy-extensions](https://github.com/flightphp/tracy-extensions) (Flight-specific Tracy panels)
- **APM (Performance Monitoring):**
  - [flightphp/apm](https://github.com/flightphp/apm) (application performance monitoring)
- **Encryption:**
  - [defuse/php-encryption](https://github.com/defuse/php-encryption) (encryption/decryption)
- **Job Queue:**
  - [n0nag0n/simple-job-queue](https://github.com/n0nag0n/simple-job-queue) (asynchronous job processing)
- **Templating:**
  - [latte/latte](https://github.com/nette/latte) (recommended templating engine)
  - (Deprecated) flightphp/core View (basic, not recommended for large projects)
- **API Documentation:**betaflightphp
  - [SwaggerUI](https://github.com/zircote/swagger-php) (Swagger/OpenAPI documentation)
  - [Flight OpenAPI Generator](https://daniel-schreiber.de/blog/flightphp-openapi-generator.html) (API-first approach)

Choose the packages that best fit your project's needs. Official Flight packages are recommended for core functionality.

## Security Best Practices (Condensed)

All code must follow secure coding practices. Always treat user input as untrusted. Key requirements:

### Cross Site Scripting (XSS)
- Always escape user output in views.
- Use Flight’s view class or a templating engine (e.g., Latte) for auto-escaping.
```php
Flight::view()->set('name', $name);
Flight::view()->render('template', ['name' => $name]);
```

### SQL Injection
- Never concatenate user input in SQL.
- Always use prepared statements or parameterized queries.
- Preferred usage for raw SQL is with flight\database\PdoWrapper
```php
$statement = Flight::db()->fetchRow('SELECT * FROM users WHERE username = :username', [':username' => $username]);
```

### CORS
- Set CORS headers via utility or middleware before `Flight::start()`.
- Only allow trusted origins.
```php
Flight::before('start', [ (new CorsUtil()), 'set' ]);
```

### Error Handling
- Don’t display sensitive errors in production; log them instead.
- Use `Flight::halt()` for controlled responses.
```php
if (ENVIRONMENT === 'production') {
    ini_set('display_errors', 0);
    ini_set('log_errors', 1);
}
Flight::halt(403, 'Access denied');
```

### Input Sanitization
- Sanitize and validate all user input.
```php
$clean_input = filter_var(Flight::request()->data->input, FILTER_SANITIZE_STRING);
```

### Password Hashing
- Always hash passwords; never store plain text.
```php
$hashed_password = password_hash($password, PASSWORD_DEFAULT);
if (password_verify($password, $stored_hash)) { /* Password matches */ }
```

### Rate Limiting
- Use caching or middleware to limit repeated requests.
```php
Flight::before('start', function() {
    $cache = Flight::cache();
    $ip = Flight::request()->ip;
    $key = "rate_limit_{$ip}";
    $attempts = (int) $cache->get($key);
    if ($attempts >= 10) Flight::halt(429, 'Too many requests');
    $cache->set($key, $attempts + 1, 60);
});
```

## Process for Adding New Subtopics

To ensure consistency, all new subtopics added to `app/config/physics_content.json` MUST follow the "Full Content" structure.

1.  **Check for Existing Content:**
    - Before generating content, search `app/config/physics_content.json` to see if the subtopic already exists.
    - **Strict Policy:** If the subtopic already exists, **DO NOT overwrite or update it.** These entries (like `conservation-of-linear-momentum`) are considered the "Gold Standard" of the project's hand-crafted style. 
    - If you believe an update is necessary, present the proposed change to the user and obtain explicit permission first.

2.  **Verify Linkability (Prerequisite):**
    - Search the `content` string of the provided `parent_topic` for the subtopic phrase (or its Title Case equivalent).
    - **Strict Policy:** If the phrase does not appear in the parent's content, **DO NOT proceed** with the creation or update. This prevents the creation of "orphaned" pages that are no longer conceptually linked in the module. Notify the user if a phrase is missing.

3.  **Generate Content Object (If Proceeding):**
    - You will always conduct **'Deep Research'** and provide comprehensive, **University level detail**. Based on the topic, generate a JSON object for the new subtopic with the following structure:
    *   **key:** The topic name converted to `kebab-case`.
    *   **`title`:** The topic name in `Title Case`.
    *   **`parent_topic`:** The `kebab-case` parent topic name provided by the user.
    *   **`content`:** A detailed, university-level explanation of the topic, formatted as an HTML string.
    *   **`formulas` (Optional):** An array of objects, each containing `title`, `equation` (LaTeX), and `breakdown` (HTML). Use this instead of the legacy `equations`/`breakdowns` fields.

3.  **Seek Approval:** Before modifying the file, present the complete, fully-formatted JSON object for the new subtopic to the user for approval.

4.  **Insert/Update File:** Once approved, programmatically read the `physics_content.json` file, add the new subtopic object to the `subtopics` map, **and update the `content` of the `parent_topic` to include a functional link to the new subtopic.** 
    *   **JSON Escaping Note:** When updating the JSON file via script (e.g., using Python's `json.dump`), ensure the strings in memory use literal double quotes for HTML attributes (e.g., `href="..."`). The library will automatically convert these to correctly escaped JSON sequences (e.g., `href=\"...\"`). Do NOT manually over-escape (avoid `\\\\\"`).

5.  **Content Quality Standards (The "Gold Standard"):**
    *   **No Linguistic Artifacts:** Never generate doubled words (e.g., "the the", "is is"). 
    *   **Contextual dimensional prefixes:** Only use dimensional descriptors (like "4D") when technically required for geometric accuracy. Do not use them as generic stylistic prefixes (e.g., avoid "4D university-level", "4D nature").
    *   **Hierarchical Integrity:** Ensure new subtopics do not create circular parent-topic references.
    *   **Mandatory Interlinking:** Every subtopic MUST be linked within the `content` string of its `parent_topic`.
    *   **Post-Update Validation:** After any modification to the data or file, you MUST run:
        ```bash
        php validate_physics_data.php
        ```
        Address any reported errors before concluding the task.

    *   **HTML Output Verification:** After the data is synchronized, you MUST verify the live HTML output using `curl` to ensure MathJax and links are rendering correctly on BOTH the new subtopic and its parent.
        ```bash
        # 1. Verify the new subtopic page
        # CHECK: Must see EXACTLY one backslash before ( or [
        # BAD: \\( or \\\[
        # GOOD: \( or \[
        curl -s http://localhost/physics/subtopic/your-slug | grep -E "\\\\\\(|\\\\\\\\\\["
        
        # 2. Verify the parent page
        curl -s http://localhost/physics/subtopic/parent-slug | grep -F "your-slug"
        ```
        - **LaTeX:** Confirm that delimiters appear as `\(` and `\[` in the raw HTML. If you see `\\(` or `\\\[`, the data is over-escaped.
        - **Links:** Confirm that `href` attributes do not contain `%22` or triple backslashes.
        - **Parent Link:** Confirm that the parent topic actually contains the correct `href` to the child and is wrapped in `<strong>` tags.

    *   **Link Preservation:** When updating or upgrading an existing subtopic, you MUST meticulously preserve all existing functional links within the `content` and `breakdown` strings. Identify all current `<a href=\"...\" ...>` tags and ensure they are either carried over exactly or correctly re-mapped to their modern slugs. Never prioritize new text over the established network of inter-links.

    *   **Formula Breakdown Verification:** Every formula entry must pass three technical checks:
        1.  **Alignment:** The `title` field must exactly match the bolded technical header within the `breakdown` string (plain text only in title). *Exception:* This rule can be relaxed if the title and header are universally recognized as synonymous or represent intrinsically linked facets of the same law (e.g., "Lorentz Force" vs "Electromagnetic Interaction").
        2.  **Header Linking:** If the subtopic phrase (or a Title Case equivalent) appears as the bolded header in the `breakdown`, it MUST be converted into a functional link: `<a href=\"/physics/subtopic/slug\" class=\"subtopic-link\"><strong>Phrase</strong></a>`.
        3.  **Accuracy:** The `equation` must be mathematically verified against standard University-level textbooks to ensure it correctly represents the technical header.
        4.  **Single Link:** Ensure only one functional link exists per formula block, residing exclusively within the `breakdown` text (usually as the header).

## The "Blob Strategy" for Context Efficiency

To maintain long-term session performance and minimize token usage when working with large datasets (like `physics_content.json`), all AI assistants MUST adhere to the **Blob Strategy**:

1.  **Local Orchestration:** Treat large data files as "blobs" that remain on the server's disk. Do NOT attempt to read or transmit the full content of files larger than 1MB into the conversation history.
2.  **Server-Side Processing:** Perform complex data operations (batch updates, global searches, interlinking) using Python or PHP scripts executed on the server. The assistant should only receive high-signal summaries of the results (e.g., "Updated 250 topics, 0 errors").
3.  **Surgical Peeking:** When inspecting data, use targeted tools like `grep_search` or `read_file` with precise `start_line` and `end_line` parameters. Never read more than 50-100 lines of a large JSON file at once.
4.  **Batch Compression:** When generating new content, use sub-agents to draft data in memory and then "blob" the final validated objects into the main file in a single atomic turn.
5.  **Navigational Health:** Regularly run local scripts to verify link integrity and rendering without loading the full link map into context.

## Subtopic Template and Linking

When creating or updating subtopics, use the following JSON template and HTML conventions to ensure University-level quality and correct site navigation.

### 1. JSON Template (Unified Structure)
Always use the `formulas` array instead of separate `equations`/`breakdowns` maps to ensure a 1-to-1 relationship and proper click-to-view functionality.

**Redundancy Rule:** To avoid over-linking and maintain a clean visual hierarchy:
*   The `title` field in the formulas array SHOULD NOT contain any HTML tags (no `<strong>`, no `<a>`). Bolding is handled automatically via CSS.
*   The primary functional link to a related subtopic should reside exclusively within the `breakdown` string, wrapped in `<strong>` tags.

```json
"subtopic-slug": {
    "title": "Title Case Name",
    "parent_topic": "parent-slug",
    "content": "<p>A comprehensive introductory paragraph (University-level) that defines the concept and its significance. Use <strong>Bold Tags</strong> for key terms and <a href=\"/physics/subtopic/related-slug\" class=\"subtopic-link\"><strong>Cross-links</strong></a> to related subtopics.</p><h3>1. Section Title</h3><p>Detailed technical explanation...</p>",
    "formulas": [
        {
            "title": "Specific Relation Name",
            "equation": "\\text{LaTeX Equation}",
            "breakdown": "<strong><a href=\"/physics/subtopic/target-slug\" class=\"subtopic-link\">Target Title</a>:</strong> Detailed explanation of symbols and physical implications."
        }
    ]
}
```

### 2. Linking Convention
To link to another subtopic within the `content` or `breakdown` strings, use the following HTML structure:
```html
<a href=\"/physics/subtopic/target-slug\" class=\"subtopic-link\"><strong>Target Title</strong></a>
```
*   **Target Slug:** The kebab-case key used in the `subtopics` map.
*   **CSS Class:** Always include `class=\"subtopic-link\"` for correct styling.
*   **Strong Tags (MANDATORY):** Always wrap the link text in `<strong>` tags for visual emphasis. This is a core part of the project's aesthetic.

### 3. MathJax Convention
Use `\\(` and `\\)` for inline math, and `\\\\[` and `\\\\]` for display-style block equations within the content string.
*   **Inline:** `\\( E = mc^2 \\)`
*   **Block:** `\\\\[ \\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\varepsilon_0} \\\\]`
*   **Formula Field:** In the `"equation"` field of the `formulas` array, use single backslashes for LaTeX (e.g., `\\nabla`) as the JSON encoder will handle the escaping.

### 4. Special Note on Quotes and Escaping
To ensure functional HTML links within the JSON data, follow these rules strictly:

*   **Manual File Editing:** If you are editing `physics_content.json` directly, HTML attributes must use escaped double quotes: `href=\"/url\"`.
*   **Programmatic Updates (Python/PHP):** When using a script to update the data, **use literal quotes in your string variables** (e.g., `s = '<a href="/url">...'`). The `json.dump` (Python) or `json_encode` (PHP) functions will automatically handle the backslash escaping for the file.
*   **Avoid Over-Escaping:** Never manually add backslashes to a string that will be passed to a JSON encoder (avoid `\\\"`). This results in `\\\"` in the file and malformed `%22` URLs in the browser.
*   **Shell Command Precaution:** When running Python one-liners from the terminal (e.g., `python3 -c '...'`), remember that the shell may consume backslashes. Always verify the resulting file content with `grep` and `cat -A` to ensure it contains exactly `\"` and not `\\\"`.
