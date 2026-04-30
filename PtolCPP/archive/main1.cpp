#include <iostream>
#include <string>
#include <vector> // Likely needed for message history
#include <mutex>  // If you plan threading for chat
#include <condition_variable> // If you plan threading for chat

// This is the CRUCIAL part for the 'OK' macro conflict.
// Undefine the 'OK' macro if it's already defined by some system header.
// This must come *before* any cpr headers are included.
#ifdef OK
#undef OK
#endif

// Now include cpr and json
#include "externals/cpr/include/cpr/cpr.h" // Adjust path if needed
#include "externals/json/single_include/nlohmann/json.hpp" // Adjust path if needed

// Ncurses includes
#include <ncursesw/ncurses.h> // Use ncursesw/ncurses.h for wide character support
#include <locale.h>           // Required for wide characters (setlocale)


// Global variables for Ncurses windows (if you're using them globally)
// It's good practice to declare them at a scope where they are accessible
// by functions that need them.
WINDOW *chat_window;
WINDOW *input_window;
WINDOW *border_window;

// Function prototypes
void setup_windows();
void cleanup_ncurses();
void print_message(WINDOW* win, const std::string& sender, const std::string& message, int color_pair);
// Add other function prototypes as needed

void std::string getGeminiApiKey() {
    const char* api_key_cstr = std::getenv("GEMINI_API_KEY");

    if (api_key_cstr == nullptr) {
        // The environment variable was not found.
        // You should handle this error appropriately.
        // For development, you might print a message and exit,
        // or prompt the user, or throw an exception.
        std::cerr << "Error: GEMINI_API_KEY environment variable not set." << std::endl;
        // Example: Throw Exception then Exit the program
        throw std::runtime_error("GEMINI_API_KEY environment variable not set.");
        exit(EXIT_FAILURE);
    }

    // Convert the C-style string to a C++ std::string
    return std::string(api_key_cstr);
}

// main function
int main() {
    setlocale(LC_ALL, ""); // Enable wide character support for Ncurses

    initscr();             // Initialize ncurses
    cbreak();              // Line buffering disabled, pass characters immediately
    noecho();              // Don't echo input characters
    keypad(stdscr, TRUE);  // Enable special keys (like arrow keys, F-keys)
    start_color();         // Enable color

    // Initialize color pairs (example)
    init_pair(1, COLOR_CYAN, COLOR_BLACK); // For sender name
    init_pair(2, COLOR_WHITE, COLOR_BLACK); // For message text

    // Set up your chat windows
    setup_windows();

    // Example usage of getmaxyx with stdscr
    int screen_max_y, screen_max_x;
    getmaxyx(stdscr, screen_max_y, screen_max_x);
    mvwprintw(chat_window, 0, 0, "Screen size: %d rows, %d cols", screen_max_y, screen_max_x);
    wrefresh(chat_window);

    std::string gemini_api_key = getGeminiApiKey();

    // Now you can use 'gemini_api_key' when making requests to the Gemini API
    // For example, adding it to your cpr::Header:
    cpr::Header headers = {
        {"Content-Type", "application/json"},
        {"x-goog-api-key", gemini_api_key} // This is likely how Gemini API expects it
    };

    // Test a cpr request (example)
    try {
        cpr::Response r = cpr::Get(cpr::Url{"http://httpbin.org/get"});
        if (r.status_code == 200) {
            print_message(chat_window, "System", "Successfully connected to httpbin.org!", 1);
            print_message(chat_window, "Debug", r.text.substr(0, 50) + "...", 2); // Print first 50 chars of response
        } else {
            print_message(chat_window, "Error", "Failed to connect: " + std::to_string(r.status_code), 1);
            print_message(chat_window, "Error Detail", r.error.message, 1);
        }
    } catch (const std::exception& e) {
        print_message(chat_window, "Exception", "CPR Exception: " + std::string(e.what()), 1);
    }
    std::cout << "API Key Successfully Loaded (first 5 chars): " << gemini_api_key.substr(0, 5) << "..." << std::endl;
    wrefresh(chat_window);


    // Main loop for chat (simplified)
    int ch;
    while ((ch = getch()) != 'q') { // Press 'q' to quit
        // Handle input, send messages, etc.
        // For now, just refresh
        wrefresh(input_window);
        wrefresh(chat_window);
    }

    cleanup_ncurses(); // Clean up Ncurses
    return 0;
}

// Function to retrieve API key from GEMINI_API_KEY env var
void 
// Function to set up Ncurses windows
void setup_windows() {
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x); // Get overall screen dimensions

    // Create a border window (optional, but good for visual separation)
    border_window = newwin(max_y, max_x, 0, 0);
    box(border_window, 0, 0); // Draw a default border
    wrefresh(border_window);

    // Chat window takes most of the screen
    chat_window = newwin(max_y - 3, max_x - 2, 1, 1); // 1 row offset, 1 col offset for border
    scrollok(chat_window, TRUE); // Enable scrolling
    wrefresh(chat_window);

    // Input window at the bottom
    input_window = newwin(1, max_x - 2, max_y - 2, 1); // 1 row high, at bottom, 1 col offset
    wrefresh(input_window);
}

// Function to clean up Ncurses
void cleanup_ncurses() {
    delwin(chat_window);
    delwin(input_window);
    delwin(border_window); // Delete border window too
    endwin(); // End ncurses mode
}

// Function to print messages to the chat window
void print_message(WINDOW* win, const std::string& sender, const std::string& message, int color_pair) {
    if (win == nullptr) return; // Basic check

    wattron(win, COLOR_PAIR(color_pair)); // Apply color for sender
    wprintw(win, "%s: ", sender.c_str());
    wattroff(win, COLOR_PAIR(color_pair)); // Turn off color

    wprintw(win, "%s\n", message.c_str()); // Print message, newline to scroll
    wrefresh(win); // Refresh the window to show changes
}
