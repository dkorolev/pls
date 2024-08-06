#pragma once

#ifndef PLS_INSTRUMENTATION

#define PLS_JOIN_HELPER(a,b) a##b
#define PLS_JOIN(a,b) PLS_JOIN_HELPER(a,b)

#define PLS_PROJECT(name) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = name;

#define PLS_INCLUDE_HEADER_ONLY_CURRENT()

#define PLS_ADD(lib,repo) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = lib; \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = repo;

#define PLS_DEP(lib) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = lib;

#define PLS_ADD_DEP(lib,repo) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = lib; \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = repo;

#else  // PLS_INSTRUMENTATION

#define PLS_PROJECT(name) PLS_INSTRUMENTATION_OUTPUT{"pls_project":name}
#define PLS_INCLUDE_HEADER_ONLY_CURRENT() PLS_INSTRUMENTATION_OUTPUT{"pls_include_header_only_current":true}
#define PLS_ADD(lib,repo) PLS_INSTRUMENTATION_OUTPUT{"pls_add":{"lib":lib,"repo":repo}}
#define PLS_DEP(name) PLS_INSTRUMENTATION_OUTPUT{"pls_dep":name}
#define PLS_ADD_DEP(lib,repo) PLS_INSTRUMENTATION_OUTPUT{"pls_add_dep":{"lib":lib,"repo":repo}}

#endif  // PLS_INSTRUMENTATION
