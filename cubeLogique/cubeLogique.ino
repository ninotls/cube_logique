#include <vector>
#include <string>
using namespace std;

// ############################ Class Definition #################################
class CubeLogique {

#define BITS 4  // Number on 4 bits
#define LED1_PIN D0
#define LED2_PIN D1
#define LED3_PIN D2
#define LED4_PIN D3

#define INTER1_PIN D5
#define INTER2_PIN D6
#define INTER3_PIN D7
#define INTER4_PIN D8

private:
  vector<bool> leds;

  void _decToBinary(uint8_t n) {
    while (n != 0) {
      if (n % 2 == 0) {
        leds.push_back(0);
      } else {
        leds.push_back(1);
      }
      n /= 2;
    }
    for (int i = leds.size(); i < BITS; i++) {
      leds.push_back(0);
    }
  }

  uint8_t _convertToPin(uint8_t eltIndex, bool led = true) {
    uint8_t pinNumber;

    switch (eltIndex) {
      case 0:
        if (led)
          pinNumber = LED1_PIN;
        else
          pinNumber = INTER1_PIN;
        break;
      case 1:
        if (led)
          pinNumber = LED2_PIN;
        else
          pinNumber = INTER2_PIN;
        break;
      case 2:
        if (led)
          pinNumber = LED3_PIN;
        else
          pinNumber = INTER3_PIN;
        break;
      case 3:
        if (led)
          pinNumber = LED4_PIN;
        else
          pinNumber = INTER4_PIN;
        break;
      default:
        break;
    }

    return pinNumber;
  }

  void _updateLedsStatus() {
    for (uint8_t i = 0; i < BITS; i++) {
      if (leds[i])
        digitalWrite(_convertToPin(i), HIGH);
      else
        digitalWrite(_convertToPin(i), LOW);
    }
    leds.clear();
  }

public:
  uint8_t getSwitchStatus(uint8_t switche, bool currentStatus) {
    uint8_t switch_status = digitalRead(_convertToPin(switche, false));
    if (currentStatus != (bool)switch_status) {
      return switch_status;
    } else {
      return currentStatus;
    }
  }

  void getAllSwitchesStatus(bool* switches) {
    for (int i = 0; i < BITS; i++) {
      switches[i] = getSwitchStatus(i, switches[i]);
    }
  }

  void displaySwitchesStatus(bool* switches) {
    for (int i = BITS - 1; i >= 0; i--)
      if (switches[i])
        Serial.print("1, ");
      else
        Serial.print("0, ");
    Serial.println();
  }

  bool checkAllSwitchesOff(bool* switches) {
    getAllSwitchesStatus(switches);
    if (!switches[0] && !switches[1] && !switches[2] && !switches[3])
      return true;
    else
      return false;
  }

  void switchAllLedsOff() {
    leds.assign(4, 0);
    _updateLedsStatus();
    leds.clear();
  }

  void ledManagement(vector<uint8_t>* sequence) {
    for (uint8_t i = 0; i < sequence->size(); i++) {
      _decToBinary(sequence->at(i));
      _updateLedsStatus();
      delay(800);
    }
  }
};

// ############################ MicroControle Code ##############################
CubeLogique* myCube = new CubeLogique();
vector<uint8_t> ledSequence;
bool switches[4] = { 0, 0, 0, 0 };
#define CMD_BUFF_LEN 255

char cmd[CMD_BUFF_LEN];

vector<string> split(string input, string delim) {
  vector<string> ret;
  string token;
  size_t search_start = 0U;
  size_t token_start = 0U;
  size_t end;

  do {
    end = input.find(delim, search_start);
    token = input.substr(token_start, end - token_start);
    search_start = end + delim.length();

    if ((token[0] != '\"') || ((token[0] == '\"') && (token[token.length() - 1] == '\"'))) {
      /* We are not in a quoted string with spaces : append the token in the result vector */
      token_start = search_start;
      if (token.length() > 0) {
        if (((token[0] == '\"') && (token[token.length() - 1] == '\"'))) {
          token = token.substr(1, token.length() - 2);
        }
        ret.push_back(token);
      }
    }
  } while (end != string::npos);

  return ret;
}

void IRAM_ATTR switch_1_updated() {
  switches[0] = myCube->getSwitchStatus(0, switches[0]);
}

void IRAM_ATTR switch_2_updated() {
  switches[1] = myCube->getSwitchStatus(1, switches[1]);
}

void IRAM_ATTR switch_3_updated() {
  switches[2] = myCube->getSwitchStatus(2, switches[2]);
}

void IRAM_ATTR switch_4_updated() {
  switches[3] = myCube->getSwitchStatus(3, switches[3]);
}

void setup() {
  Serial.begin(115200);

  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(LED3_PIN, OUTPUT);
  pinMode(LED4_PIN, OUTPUT);

  pinMode(INTER1_PIN, INPUT);
  pinMode(INTER2_PIN, INPUT);
  pinMode(INTER3_PIN, INPUT);
  pinMode(INTER4_PIN, INPUT);

  attachInterrupt(digitalPinToInterrupt(INTER1_PIN), switch_1_updated, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INTER2_PIN), switch_2_updated, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INTER3_PIN), switch_3_updated, CHANGE);
  attachInterrupt(digitalPinToInterrupt(INTER4_PIN), switch_4_updated, CHANGE);

  // switch off all LEDS
  myCube->switchAllLedsOff();

  // Chenillard
  ledSequence = { 15, 0, 1, 2, 4, 8, 4, 2, 1, 15, 0, 15, 0 };
  myCube->ledManagement(&ledSequence);
  ledSequence.clear();

  while (!myCube->checkAllSwitchesOff(switches)) {
    Serial.println("Tous les interupteurs ne sont pas en position haute");
    delay(1000);
  }
  Serial.println("Le cube est en attente de commande...");
}

void loop() {
  // Parse incoming command
  if (Serial.available() > 0) {
    size_t dataRead = Serial.readBytes(cmd, CMD_BUFF_LEN);
    string myCommand = string(cmd, dataRead);

    vector<string> tokens = split(myCommand, " ");

    if (tokens.size() > 0) {
      string command = tokens[0];

      // Parsing all commands
      if (command == "leds") {
        for (int i = 1; i < tokens.size(); i++)
          ledSequence.push_back(atoi(tokens[i].c_str()));
        myCube->ledManagement(&ledSequence);
        ledSequence.clear();
        Serial.println("LEDS UPDATED");
        return;
      } else if (command == "switches") {
        myCube->getAllSwitchesStatus(switches);
        myCube->displaySwitchesStatus(switches);
        Serial.println("DONE");
        return;
      } else if (command == "rst") {
        ESP.reset();
        Serial.println("DONE");
        return;
      } else
        Serial.println("Unknown command");
    }
    return;
  }
}