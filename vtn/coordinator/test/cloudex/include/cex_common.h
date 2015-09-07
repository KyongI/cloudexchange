//cex_common.h
//
//REF : coordinator/modules/restjsonutil/include/rest_common_defs.hh

#ifndef CEX_COMMON_DEFS_H_
#define CEX_COMMON_DEFS_H_

#include <string>

#define CONTENT_TYPE "Content-type: application/json"
#define ACCEPT_TYPE "Accept: application/json"

const char PROTOCOL[] = "http://";
const char COLON[] = ":";
const size_t SIZE_NULL = 0;
const int ZERO_ARRAY_LENGTH = 0;
const int CURLOPT_ENABLE = 1;
const int CURLOPT_DISABLE = 0;

typedef enum {
  HTTP_METHOD_POST = 1,
  HTTP_METHOD_PUT,
  HTTP_METHOD_DELETE,
  HTTP_METHOD_GET,
} HttpMethod;

typedef struct {
  char *memory;
  int size;
} HttpContent_t;

typedef struct {
  int code;
  HttpContent_t *write_data;
} HttpResponse_t;

typedef enum {
  REST_OP_SUCCESS = 0,
  REST_OP_FAILURE
} rest_resp_code_t;

typedef struct {
  uint32_t odc_port;
  uint32_t request_time_out;
  uint32_t connection_time_out;
  std::string user_name;
  std::string password;
} ConfFileValues_t;

#endif //CEX_COMMON_DEFS_H_
