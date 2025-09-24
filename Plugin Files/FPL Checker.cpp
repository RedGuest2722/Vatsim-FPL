#include "EuroScopePlugIn.h"
#include <websocketpp/config/asio_no_tls_client.hpp>
#include <websocketpp/client.hpp>
#include <string>
#include <sstream>
#include <json/json.h> // Or use nlohmann/json if preferred

using namespace EuroScopePlugIn;
typedef websocketpp::client<websocketpp::config::asio_client> client;

class PythonBridgePlugin : public CPlugIn {
public:
    PythonBridgePlugin() : CPlugIn("PythonBridgePlugin", "Will", "Sends flight plan via WebSocket") {}

    void RadarScreenLoaded() override {
        DisplayUserMessage("PythonBridge", "Radar screen loaded", "Plugin initialized.");
    }

    void FlightPlanControllerAssigned(CFlightPlan FlightPlan) override {
        std::string depICAO = FlightPlan.GetFlightPlanData().GetDepartureICAO();
        std::string myICAO = GetPlugInScreen()->GetICAO();

        if (depICAO == myICAO) {
            std::string callsign = FlightPlan.GetCallsign();
            std::string destICAO = FlightPlan.GetFlightPlanData().GetDestinationICAO();

            // Build JSON payload
            Json::Value root;
            root["event"] = "departure_assigned";
            root["callsign"] = callsign;
            root["departure"] = depICAO;
            root["destination"] = destICAO;

            Json::StreamWriterBuilder writer;
            std::string jsonStr = Json::writeString(writer, root);

            // Send via WebSocket
            try {
                client wsClient;
                wsClient.init_asio();

                websocketpp::connection_hdl hdl;
                wsClient.set_open_handler([&wsClient, jsonStr](websocketpp::connection_hdl hdl) {
                    wsClient.send(hdl, jsonStr, websocketpp::frame::opcode::text);
                    wsClient.close(hdl, websocketpp::close::status::normal, "Done");
                });

                websocketpp::lib::error_code ec;
                client::connection_ptr con = wsClient.get_connection("ws://localhost:25555", ec);
                if (ec) return;

                wsClient.connect(con);
                wsClient.run();
            } catch (...) {
                DisplayUserMessage("PythonBridge", "WebSocket Error", "Failed to send flight plan.");
            }
        }
    }
};

PythonBridgePlugin pluginInstance