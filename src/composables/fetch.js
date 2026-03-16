// START_FEATURE vue
import { useCSRF } from "./csrf.js"

export function useFetch() {
  const { csrf } = useCSRF()
  const post = (url, options = {}, headers = {}) => {
    return fetch(url, {
      headers: {
        ...headers,
        "X-CSRFTOKEN": csrf.value,
      },
      ...{
        method: "POST",
        ...options,
      },
    })
  }
  const get = (url, options = {}, headers = {}, queryParams = {}) => {
    let searchParams = new URLSearchParams(queryParams)
    return fetch(url + "?" + searchParams.toString(), {
      headers,
      ...{
        method: "GET",
        ...options,
      },
    })
  }
  const poll = async (
    valueRef,
    url,
    handleResponse = null,
    onSuccess = null,
    pollRate = 2000,
    options = {},
    headers = {},
    queryParams = {},
  ) => {
    const doQuery = async () => {
      return await get(url, options, headers, queryParams).then(async res => {
        if (res.status === 202) {
          return false
        } else {
          if (handleResponse) {
            return await handleResponse(res)
          }
          return await res.json()
        }
      })
    }
    const tryAgain = () => {
      setTimeout(async () => {
        const res = await doQuery()
        if (res !== false) {
          valueRef.value = res
        } else {
          tryAgain()
        }
      }, pollRate)
    }
    tryAgain()
  }
  return { post, get, poll }
}
// END_FEATURE vue
