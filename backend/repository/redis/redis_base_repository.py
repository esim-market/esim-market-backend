from abc import ABC, abstractmethod
from typing import Any


class RedisBaseRepository(ABC):
    """Async Redis repository contract shared by standalone and Sentinel modes."""

    @abstractmethod
    def _read(self): ...

    @abstractmethod
    def _write(self): ...

    async def set(self, key, value, exp_after_secs: int | None = None):
        result = await self._write().set(key, value)
        if exp_after_secs is not None: await self._write().expire(key, exp_after_secs)
        return result

    async def get(self, key): return await self._read().get(key)
    async def append_stream_item(self, stream_name: str, data: dict): return await self._write().xadd(stream_name, data)
    async def delete_stream_item(self, stream_name: str, entry_ids: list[str]): return await self._write().xdel(stream_name, *entry_ids)
    async def consume_stream(self, stream_name, last_id, item_count=None, block_in_ms=None):
        kw = {k: v for k, v in (("count", item_count), ("block", block_in_ms)) if v is not None}
        return await self._read().xread({stream_name: last_id}, **kw)
    async def consume_stream_safe(self, stream_name, groupname, consumername, item_count=1, block_in_ms=None):
        kw = {k: v for k, v in (("count", item_count), ("block", block_in_ms)) if v is not None}
        return await self._write().xreadgroup(groupname, consumername, {stream_name: ">"}, **kw)
    async def claim_stream_messages(self, stream_name, groupname, consumername, min_idle_time, start_id, count):
        return await self._write().xautoclaim(stream_name, groupname, consumername, min_idle_time, start_id, count=count)
    async def get_stream(self, key): return await self._read().xrevrange(key, min="-", max="+")
    async def get_sorted_set(self, key, master=False): return await (self._write() if master else self._read()).zrevrange(key, 0, -1, withscores=True)
    async def append_sorted_set(self, name, mapping): return await self._write().zadd(name, mapping=mapping)
    async def get_hash(self, name, key=None): return await (self._read().hgetall(name) if key is None else self._read().hget(name, key))
    async def ping(self): return await self._write().ping()
    async def set_hash(self, name, mapping, exp_after_secs=None):
        result = await self._write().hset(name, mapping=mapping)
        if exp_after_secs is not None: await self._write().expire(name, exp_after_secs)
        return result
    async def get_keys(self, pattern="*"): return await self._read().keys(pattern)
    async def delete_keys(self, keys): return await self._write().delete(*keys)
    async def delete_sorted_set_item(self, name, items): return await self._write().zrem(name, *items)
    async def set_json(self, key, mapping, exp_after_secs=None): raise NotImplementedError("RedisJSON requires Redis Stack")
    async def get_json(self, key): raise NotImplementedError("RedisJSON requires Redis Stack")
    async def set_cache_json(self, key, mapping, exp_after_secs=None):
        import json
        return await self.set(key, json.dumps(mapping), exp_after_secs)
    async def get_cache_json(self, key):
        import json
        value = await self.get(key)
        return json.loads(value) if value is not None else None
    async def create_group(self, key, gname, id="0", mkstream=False):
        if not await self.is_group_exists(key, gname): await self._write().xgroup_create(key, gname, id=id, mkstream=mkstream)
    async def is_group_exists(self, key, gname): return any(item["name"] == gname for item in await self._write().xinfo_groups(key))
    async def ack_stream_message(self, key, groupname, ids): return await self._write().xack(key, groupname, *ids)
    async def get_stream_ack_pending(self, stream_name, groupname, min_id, max_id, count=1): return await self._write().xpending_range(stream_name, groupname, min=min_id, max=max_id, count=count)
    async def get_group_infos_of_stream(self, stream_name): return await self._write().xinfo_groups(stream_name)
    async def get_set(self, key, master=False):
        values = await (self._write() if master else self._read()).smembers(key)
        return list(values) if values else None
    async def set_set(self, key, value): return await self._write().sadd(key, *value)
    async def register_script(self, script): return self._write().register_script(script)
    async def execute_script(self, lua_script, keys, args): return await lua_script(keys=keys, args=args)
    async def execute_command(self, command, key, **kwargs): return await self._write().execute_command(command, key, **kwargs)
