""全局枚举定义"""
from enum import Enum


class _FlexibleEnum(str, Enum):
    """
    可同时接受 .value（英文大写）和 .label（中文）输入的枚举基类。
    """

    @classmethod
    def from_any(cls, val):
        if isinstance(val, cls):
            return val
        if not isinstance(val, str):
            raise ValueError(f'cannot construct {cls.__name__} from {type(val)}')
        s = val.strip()
        for e in cls:
            if e.value == s:
                return e
        for e in cls:
            if e.label == s:
                return e
        s_norm = s.replace(' ', '').replace('_', '').lower()
        for e in cls:
            if e.value.replace('_', '').lower() == s_norm or e.label.replace(' ', '').lower() == s_norm:
                return e
        raise ValueError(f'unknown {cls.__name__}: {val!r}')


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    OPERATOR = 'OPERATOR'
    VIEWER = 'VIEWER'

    @property
    def can_write(self) -> bool:
        return self in (UserRole.ADMIN, UserRole.OPERATOR)

    @property
    def can_manage_users(self) -> bool:
        return self == UserRole.ADMIN


class NetworkType(_FlexibleEnum):
    IP_METRO = 'IP_METRO'
    MSTP = 'MSTP'
    PTN = 'PTN'
    SDH = 'SDH'
    BARE_FIBER = 'BARE_FIBER'
    OTHER = 'OTHER'

    @property
    def label(self) -> str:
        return {
            'IP_METRO': 'IP 城域网', 'MSTP': 'MSTP 多业务传送平台',
            'PTN': 'PTN 分组传送网', 'SDH': 'SDH 同步数字体系',
            'BARE_FIBER': '裸纤', 'OTHER': '其他承载网',
        }[self.value]


class NetworkNodeRole(_FlexibleEnum):
    CORE = 'CORE'
    AGGREGATION = 'AGGREGATION'
    ACCESS = 'ACCESS'
    SITE = 'SITE'
    POI = 'POI'

    @property
    def label(self) -> str:
        return {
            'CORE': '核心节点', 'AGGREGATION': '汇聚节点',
            'ACCESS': '接入节点', 'SITE': '机房站点', 'POI': 'POI 点',
        }[self.value]


class BusinessType(_FlexibleEnum):
    ENTERPRISE = 'ENTERPRISE'
    CONSUMER_BROADBAND = 'CONSUMER_BROADBAND'
    GOVERNMENT = 'GOVERNMENT'
    OTHER = 'OTHER'

    @property
    def label(self) -> str:
        return {
            'ENTERPRISE': '政企专线', 'CONSUMER_BROADBAND': '家庭宽带',
            'GOVERNMENT': '政府单位', 'OTHER': '其他',
        }[self.value]


class CpeDeviceType(_FlexibleEnum):
    FIBER_MEDIA_CONVERTER = 'FIBER_MEDIA_CONVERTER'
    ONU = 'ONU'
    ONT = 'ONT'
    SWITCH = 'SWITCH'
    ROUTER = 'ROUTER'
    BARE_FIBER_ENDPOINT = 'BARE_FIBER_ENDPOINT'
    OTHER = 'OTHER'

    @property
    def label(self) -> str:
        return {
            'FIBER_MEDIA_CONVERTER': '光纤收发器', 'ONU': 'ONU', 'ONT': 'ONT',
            'SWITCH': '交换机', 'ROUTER': '路由器', 'BARE_FIBER_ENDPOINT': '裸纤端点',
            'OTHER': '其他',
        }[self.value]


class MediaType(_FlexibleEnum):
    FIBER = 'FIBER'
    CAT5E = 'CAT5E'
    CAT6 = 'CAT6'
    WIRELESS = 'WIRELESS'
    COAXIAL = 'COAXIAL'
    OTHER = 'OTHER'

    @property
    def label(self) -> str:
        return {
            'FIBER': '光纤', 'CAT5E': '超五类网线', 'CAT6': '六类网线',
            'WIRELESS': '无线', 'COAXIAL': '同轴', 'OTHER': '其他',
        }[self.value]
