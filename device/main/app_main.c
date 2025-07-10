/* MQTT (over TCP) Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <time.h>
#include "esp_wifi.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include "driver/gpio.h"
#include "cJSON.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "esp_log.h"
#include "mqtt_client.h"


#define LED_PIN GPIO_NUM_2 // GPIO2 es el LED integrado en muchas ESP32
#define HOST "192.168.100.30"
#define PORT 8883
#define NAME "custom-device3"

static const char *ca_cert_pem = 
"-----BEGIN CERTIFICATE-----\n"
"-----END CERTIFICATE-----\n";

static int led_state = 0; // 0 = apagado, 1 = encendido

static char* message = "initial";
// Función para inicializar el LED
void init_led() {
    gpio_reset_pin(LED_PIN);                // Resetea la configuración del pin
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT); // Configura el pin como salida
    gpio_set_level(LED_PIN, led_state);     // Establece el estado inicial
}

static const char *TAG = "mqtt_example";


static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0) {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}


void generate_random_number_task(void *pvParameters) {
    
    esp_mqtt_client_handle_t client = (esp_mqtt_client_handle_t)pvParameters;

    // Inicializa la semilla para la generación de números aleatorios
    srand((unsigned int)time(NULL));
    int msg_id;
    char number_str[256]; // Buffer para almacenar el número como string
    while (1) {
        float random_number = 10.0f + ((float)rand() / (float)RAND_MAX) * (100.0f - 10.0f);
        sprintf(number_str, "{\"randnum\" : %f, \"message\" : \"%s\", \"ping\" : \"pong\"}", random_number, message); // Convierte el número a string
        msg_id = esp_mqtt_client_publish(client, "incoming/data/" NAME "/values", number_str, 0, 0, 0);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        vTaskDelay(pdMS_TO_TICKS(10000)); // Espera 5 segundos
    }
}


void handle_response(esp_mqtt_event_handle_t event, esp_mqtt_client_handle_t client) {
    if (event->event_id != MQTT_EVENT_DATA) {
        return;
    }
    char topic_buffer[event->topic_len + 1];
    // Copiar el tema del evento a la variable
    memcpy(topic_buffer, event->topic, event->topic_len);
    topic_buffer[event->topic_len] = '\0';
    ESP_LOGI(TAG, "Received Data: %s", topic_buffer );
    char *tokens[6];
    char *token;
    char *cmd;
    char *method;
    char *uuid;
    int i = 0;
    token = strtok(topic_buffer, "/");
    while (token != NULL && i < 6) {
        tokens[i++] = token;
        ESP_LOGI(TAG, "Token[%d]: %s", i - 1, token);  // Imprimir el token
        token = strtok(NULL, "/");
    }
    if (i < 5) {
        ESP_LOGE(TAG, "Invalid Topic");
        return;
    }

    cmd = tokens[2];
    method = tokens[3];
    uuid = tokens[4];

    // Copiar y null-terminar el payload
    char data_buffer[event->data_len + 1];
    memcpy(data_buffer, event->data, event->data_len);
    data_buffer[event->data_len] = '\0';

    ESP_LOGI(TAG, "Payload recibido: %s", data_buffer);

    
    char response[512] = "{}"; // JSON de respuesta
    double randnum = 12.123;
    // Lógica basada en method y cmd
    if (strcmp(method, "set") == 0) {
        // Parsear JSON
        cJSON *json = cJSON_Parse(data_buffer);
        if (!json) {
            ESP_LOGE(TAG, "Error al parsear JSON");
            return;
        }
        if (strcmp(cmd, "switch") == 0) {
            cJSON *sw = cJSON_GetObjectItemCaseSensitive(json, "switch");
            ESP_LOGI(TAG, "switch");
            if (cJSON_IsBool(sw)) {
                if (cJSON_IsTrue(sw)) {
                    gpio_set_level(LED_PIN, 1);
                } else if (cJSON_IsFalse(sw)) {
                    gpio_set_level(LED_PIN, 0);
                }
            }
        } else if (strcmp(cmd, "message") == 0) {
            cJSON *msg = cJSON_GetObjectItemCaseSensitive(json, "message");
            if (cJSON_IsString(msg)) {
                message = msg->valuestring;
            }
        }
        
    } else {
        if (strcmp(cmd, "randnum") == 0) {
            ESP_LOGI(TAG, "randnum");
            fflush(stdout);
            snprintf(response, sizeof(response), "{\"randnum\": %.3f}", randnum);
        } else if (strcmp(cmd, "ping") == 0) {
            ESP_LOGI(TAG, "ping");
            fflush(stdout);
            snprintf(response, sizeof(response), "{\"ping\": %s}", "\"pong\"");
        } else if (strcmp(cmd, "message") == 0) {
            ESP_LOGI(TAG, "message");
            fflush(stdout);
            snprintf(response, sizeof(response), "{\"message\": \"%s\"}", message);
        }
        
    }
    fflush(stdout);
    char sendTopic[256];
    snprintf(sendTopic, sizeof(sendTopic), "command/response/%s", uuid);
    esp_mqtt_client_publish(client, sendTopic, response, 0, 0, 0);
}

/*
 * @brief Event handler registered to receive MQTT events
 *
 *  This function is called by the MQTT client event loop.
 *
 * @param handler_args user data registered to the event.
 * @param base Event base for the handler(always MQTT Base in this example).
 * @param event_id The id for the received event.
 * @param event_data The data for the event, esp_mqtt_event_handle_t.
 */
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32 "", base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;
    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED:
        init_led();
        // ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        // msg_id = esp_mqtt_client_publish(client, "/topic/qos1", "data_3", 0, 1, 0);
        // ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_subscribe(client, "/topic/qos0", 0);
        // ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_subscribe(client, "/topic/qos1", 1);
        // ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_unsubscribe(client, "/topic/qos1");
        // ESP_LOGI(TAG, "sent unsubscribe successful, msg_id=%d", msg_id);

        msg_id = esp_mqtt_client_subscribe(client, "command/" NAME "/#", 2);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        xTaskCreate(
            generate_random_number_task, // Función de la tarea
            "GenerateRandomNumber",      // Nombre de la tarea
            2048,                        // Tamaño de la pila
            client,                       // Parámetro pasado a la tarea
            5,                           // Prioridad de la tarea
            NULL                         // Identificador de la tarea (opcional)
        );
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        msg_id = esp_mqtt_client_publish(client, "/topic/qos0", "data", 0, 0, 0);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        ESP_LOGI(TAG, "TOPIC=%.*s\r\n", event->topic_len, event->topic);
        ESP_LOGI(TAG, "DATA=%.*s\r\n", event->data_len, event->data);
        handle_response(event, client);
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT) {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno",  event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));

        }
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
}

static void mqtt_app_start(void)
{
    char uri[128];
    // Formatear la URI con la IP y el puerto
    snprintf(uri, sizeof(uri), "mqtts://%s:%d", HOST, PORT);
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = uri,
        .broker.verification.certificate = ca_cert_pem,  // <- aquí se acepta el cert
    };
    ESP_LOGI(TAG, "%s", uri);
    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_cfg);
    /* The last argument may be used to pass data to the event handler, in this example mqtt_event_handler */
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client);
}


void app_main(void)
{
    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("mqtt_client", ESP_LOG_VERBOSE);
    esp_log_level_set("mqtt_example", ESP_LOG_VERBOSE);
    esp_log_level_set("transport_base", ESP_LOG_VERBOSE);
    esp_log_level_set("esp-tls", ESP_LOG_VERBOSE);
    esp_log_level_set("transport", ESP_LOG_VERBOSE);
    esp_log_level_set("outbox", ESP_LOG_VERBOSE);

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    mqtt_app_start();
}
