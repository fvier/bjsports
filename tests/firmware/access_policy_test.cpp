#include <initializer_list>
#include "../../firmware/esp32_catraca/access_policy.h"
#include <assert.h>
#include <stdio.h>
int main() {
  const char* token = "0123456789abcdef0123456789abcdef";
  assert(!bj::validBearer("", token));
  assert(!bj::validBearer("Bearer wrong", token));
  assert(!bj::validBearer("prefix0123456789abcdef0123456789abcdef", token));
  assert(!bj::validBearer("Bearer 0123456789abcdef0123456789abcdefEXTRA", token));
  assert(bj::validBearer("Bearer 0123456789abcdef0123456789abcdef", token));
  assert(!bj::validToken("bjsports-catraca-secret"));
  assert(!bj::validToken("0123456789abcdef0123456789abcde "));
  assert(!bj::validPulse(299)); assert(bj::validPulse(300));
  assert(bj::validPulse(3000)); assert(!bj::validPulse(3001));
  uint32_t n;
  for (auto s : {"", "-1", "1000x", " 300", "4294967296", "999999999999999999999"}) assert(!bj::parseUnsigned(s, n));
  assert(bj::parseUnsigned("4294967295", n) && n == UINT32_MAX);
  assert(bj::validDeadline(100, 5100)); assert(!bj::validDeadline(100, 100));
  assert(!bj::validDeadline(100, 99)); assert(!bj::validDeadline(100, 10101));
  assert(bj::validDeadline(UINT32_MAX - 100, 100));
  assert(bj::validCommandId("28e46453-49ad-4cae-a519-ad8932983013"));
  assert(!bj::validCommandId("short")); assert(!bj::validCommandId("abcdefghijklmnop\""));
  puts("access policy: all checks passed");
}
