# OPC UA Live Replay

The replay server publishes imported Rieth Tennessee Eastman observations under namespace `urn:processgraph:sentinel:tep`. Each of the 52 tags is a read-only OPC UA variable with source timestamps, server timestamps, status codes, descriptions, units, and type metadata. The collector creates monitored-item subscriptions, reconnects with bounded exponential backoff, persists three timestamps and quality, and records consumer offsets.

The development replay endpoint permits unencrypted local networking inside Docker. It must not be exposed outside the development host. A plant deployment requires application certificates, trust lists, authenticated identities, network allow-listing, and a technically read-only server account.
