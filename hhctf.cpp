#include <iostream>

using namespace std;

int main() {

    vector<int> encoded = {5, 50, 58, 12, 7, 38, 62, 58, 12, 7, 60, 12, 3, 33, 60};

    char key;
    cout << "Enter your key (single character): ";
    cin >> key;

    string decoded = "";
    for (int i = 0; i <= encoded.size(); i++) {
        char ch = encoded[i] ^ key;
        decoded += ch;
    }

    cout << "Your flag is: HHCTF{" << decoded << "}" << endl;
    return 0;
}
