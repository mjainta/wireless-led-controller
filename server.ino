#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

ESP8266WebServer server(80); //Web server object. Will be listening in port 80 (default for HTTP)

const char *ssid = "";
const char *password = "";

uint8_t bluePin = D1, greenPin = D2, redPin = D3;
int currentRed, currentGreen, currentBlue = 0;

void setup()
{
    //Reset all pins to 1, then 0, on start so that its reset truly
    analogWrite(redPin, 1);
    analogWrite(greenPin, 1);
    analogWrite(bluePin, 1);
    analogWrite(redPin, 0);
    analogWrite(greenPin, 0);
    analogWrite(bluePin, 0);

    Serial.begin(115200);
    WiFi.begin(ssid, password); //Connect to the WiFi network

    while (WiFi.status() != WL_CONNECTED)
    { //Wait for connection
        delay(500);
        Serial.println("Waiting to connect…");
    }

    Serial.print("IP address: ");
    Serial.println(WiFi.localIP()); //Print the local IP to access the server

    server.on("/setColor", setColorCall); //Associate the handler function to the path

    server.begin(); //Start the server
    Serial.println("Server listening");
}

void loop()
{
    server.handleClient(); //Handling of incoming requests
}

void setColorCall()
{
    String message = "";

    int red = 0, green = 0, blue = 0, fadeTime = 0;

    if (server.arg("RED") == "")
    {
        message += "RED not found";
    }
    else
    {
        message += "RED Argument = ";
        message += server.arg("RED");
        red = server.arg("RED").toInt();
    }

    message += "</br>";

    if (server.arg("BLUE") == "")
    {
        message += "BLUE not found";
    }
    else
    {
        message += "BLUE Argument = ";
        message += server.arg("BLUE");
        blue = server.arg("BLUE").toInt();
    }

    Serial.println("Server listening");
    message += "</br>";

    if (server.arg("GREEN") == "")
    {
        message += "GREEN not found";
    }
    else
    {
        message += "GREEN Argument = ";
        message += server.arg("GREEN");
        green = server.arg("GREEN").toInt();
    }

    message += "</br>";

    if (server.arg("FADE_TIME") == "")
    {
        message += "FADE_TIME not found";
    }
    else
    {
        message += "FADE_TIME Argument = ";
        message += server.arg("FADE_TIME");
        fadeTime = server.arg("FADE_TIME").toInt();
    }

    setColor(red, green, blue, fadeTime);
    currentRed = red;
    currentGreen = green;
    currentBlue = blue;

    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "text/plain", message); //Returns the HTTP response
}

void setColor(int red, int green, int blue, int fadeTime)
{
    // Calculate how many ticks we need
    int tickDelay = 50;
    int ticks = max(1, fadeTime / tickDelay);

    // Calculate how much we have to change in each tick
    double diffRed = 0, diffGreen = 0, diffBlue = 0;
    diffRed = (double)red - currentRed;
    diffGreen = (double)green - currentGreen;
    diffBlue = (double)blue - currentBlue;
    double diffTickRed = diffRed / (double)ticks;
    double diffTickGreen = diffGreen / (double)ticks;
    double diffTickBlue = diffBlue / (double)ticks;

    double tickRgb[] = {0.0, 0.0, 0.0};

        Serial.println("currentRed" + String(currentRed));
        Serial.println("wantedRed" + String(red));
        Serial.println("diffRed" + String(diffRed));
        Serial.println("currentgreen" + String(currentGreen));
        Serial.println("wantedGreen" + String(green));
        Serial.println("diffGreen" + String(diffGreen));
        Serial.println("currentblue" + String(currentBlue));
        Serial.println("wantedBlue" + String(blue));
        Serial.println("diffBlue" + String(diffBlue));
        Serial.println("diffTickRed:" + String(diffTickRed));
        Serial.println("diffTickGreen:" + String(diffTickGreen));
        Serial.println("diffTickBlue:" + String(diffTickBlue));
        Serial.println("ticks:" + String(ticks));

    for(int i = 0; i <= ticks; i++)
    {
        // Calculate the value for each color for the current tick.
        tickRgb[0] = tickRgb[0] + diffTickRed;
        tickRgb[1] = tickRgb[1] + diffTickGreen;
        tickRgb[2] = tickRgb[2] + diffTickBlue;

        analogWrite(redPin, validatePwmValue(currentRed + (int)tickRgb[0]));
        analogWrite(greenPin, validatePwmValue(currentGreen + (int)tickRgb[1]));
        analogWrite(bluePin, validatePwmValue(currentBlue + (int)tickRgb[2]));

        delay(tickDelay);
    }

    // To avoid problems with misscalculations, set the desired color at the end anyway.
    analogWrite(redPin, validatePwmValue(red));
    analogWrite(greenPin, validatePwmValue(green));
    analogWrite(bluePin, validatePwmValue(blue));
}

int validatePwmValue(int value)
{
    return max(0, min(1023, value));
}
