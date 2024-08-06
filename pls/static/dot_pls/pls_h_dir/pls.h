#pragma once

#ifndef PLS_INSTRUMENTATION

#define PLS_JOIN_HELPER(a,b) a##b
#define PLS_JOIN(a,b) PLS_JOIN_HELPER(a,b)

#define PLS_PROJECT(name) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = name;

#define PLS_INCLUDE_HEADER_ONLY_CURRENT()

#define PLS_IMPORT(lib,repo) \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = lib; \
  constexpr static char const* const PLS_JOIN(kPlsString,__COUNTER__) = repo;

#else  // PLS_INSTRUMENTATION

#define PLS_PROJECT(name) PLS_INSTRUMENTATION_OUTPUT{"pls_project":name}
#define PLS_INCLUDE_HEADER_ONLY_CURRENT() PLS_INSTRUMENTATION_OUTPUT{"pls_include_header_only_current":true}
#define PLS_IMPORT(lib,repo) PLS_INSTRUMENTATION_OUTPUT{"pls_import_deprecate_me":{"lib":lib,"repo":repo}}

#endif  // PLS_INSTRUMENTATION
