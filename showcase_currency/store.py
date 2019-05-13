

def _rate_key(source, target):
    return f'{source.upper()}:{target.upper()}'


class CurrencyUploader:

    def __init__(self, redis, replace=False):
        self.transaction = redis.multi_exec()
        if replace:
            self.transaction.flushall()

    def save(self, source, target, rate):
        key = _rate_key(source, target)
        self.transaction.set(key, rate)

    async def execute(self):
        await self.transaction.execute()


async def currency_convert(redis, source, target, amount):
    rate = await redis.get(_rate_key(source, target))
    if rate is None:
        rate = await redis.get(_rate_key(target, source))
        if rate is None:
            raise KeyError('No valid conversion rate found')
        rate = 1 / float(rate.decode())
    else:
        rate = float(rate.decode())
    return amount * rate