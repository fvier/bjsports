#pragma once
#include <stdint.h>
#include <string.h>
namespace bj {
inline bool validPulse(uint32_t value) { return value >= 300 && value <= 3000; }
inline bool parseUnsigned(const char* value, uint32_t& out) {
  if (!value || !*value) return false;
  uint64_t result = 0;
  for (const char* p = value; *p; ++p) {
    if (*p < '0' || *p > '9') return false;
    result = result * 10 + (*p - '0');
    if (result > UINT32_MAX) return false;
  }
  out = uint32_t(result); return true;
}
inline bool validToken(const char* token) {
  size_t len = strlen(token);
  if (len < 32 || len > 128) return false;
  for (size_t i = 0; i < len; i++) if (token[i] < 33 || token[i] > 126) return false;
  return true;
}
inline bool validBearer(const char* header, const char* token) {
  if (!validToken(token) || strncmp(header, "Bearer ", 7) || strlen(header + 7) != strlen(token)) return false;
  unsigned char diff = 0;
  for (size_t i = 0; i < strlen(token); ++i) diff |= header[i + 7] ^ token[i];
  return diff == 0;
}
inline bool validCommandId(const char* id) {
  size_t len = strlen(id);
  if (len < 16 || len > 64) return false;
  for (size_t i = 0; i < len; ++i) {
    char c = id[i];
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-')) return false;
  }
  return true;
}
inline bool validDeadline(uint32_t now, uint32_t deadline) {
  int32_t remaining = int32_t(deadline - now);
  return remaining > 0 && remaining <= 10000;
}
}
