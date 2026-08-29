Add a rate limiter to the upload endpoint. Make it configurable and flexible so we can swap
strategies later — token bucket now, maybe sliding window or leaky bucket down the line.
