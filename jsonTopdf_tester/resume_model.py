import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class Social:
    name: str
    link: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Social":
        return Social(
            name=data["name"],
            link=data["link"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "link": self.link}


@dataclass
class PersonalInformation:
    name: str
    email: str
    phone: str
    location: str
    socials: List[Social] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PersonalInformation":
        socials = [Social.from_dict(s) for s in data.get("socials", [])]
        return PersonalInformation(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            location=data["location"],
            socials=socials,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "socials": [s.to_dict() for s in self.socials],
        }


@dataclass
class Experience:
    designation: str
    companyName: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    caption: Optional[str] = ""
    points: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Experience":
        return Experience(
            designation=data["designation"],
            companyName=data["companyName"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            caption=data.get("caption", ""),
            points=data.get("points", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "designation": self.designation,
            "companyName": self.companyName,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date or "",
            "caption": self.caption or "",
            "points": self.points,
        }


@dataclass
class Education:
    institution: str
    degree: str
    location: str
    start_date: str
    end_date: Optional[str] = None
    gpa: str
    gpa_out_off: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Education":
        return Education(
            institution=data["institution"],
            degree=data["degree"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            gpa=data["gpa"],
            gpa_out_off=data["gpa_out_off"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "institution": self.institution,
            "degree": self.degree,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date or "",
            "gpa": self.gpa,
            "gpa_out_off": self.gpa_out_off,
        }


@dataclass
class Skill:
    name: str
    data: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Skill":
        return Skill(
            name=data["name"],
            data=data.get("data", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data": self.data,
        }


@dataclass
class ExternalSource:
    name: str
    link: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExternalSource":
        return ExternalSource(
            name=data["name"],
            link=data["link"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "link": self.link}


@dataclass
class Project:
    projectName: str
    caption: Optional[str]
    location: str
    start_date: str
    end_date: Optional[str]
    url: Optional[str]
    projectDetails: List[str] = field(default_factory=list)
    externalSources: List[ExternalSource] = field(default_factory=list)
    technologiesUsed: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Project":
        return Project(
            projectName=data["projectName"],
            caption=data.get("caption", ""),
            location=data["location"],
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            url=data.get("url", ""),
            projectDetails=data.get("projectDetails", []),
            externalSources=[ExternalSource.from_dict(es) for es in data.get("externalSources", [])],
            technologiesUsed=data.get("technologiesUsed", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectName": self.projectName,
            "caption": self.caption or "",
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date or "",
            "url": self.url or "",
            "projectDetails": self.projectDetails,
            "externalSources": [es.to_dict() for es in self.externalSources],
            "technologiesUsed": self.technologiesUsed,
        }


@dataclass
class Certification:
    name: str
    issuing_organization: str
    issue_date: str
    expiration_date: str
    credential_id: str
    url: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Certification":
        return Certification(
            name=data["name"],
            issuing_organization=data["issuing_organization"],
            issue_date=data["issue_date"],
            expiration_date=data["expiration_date"],
            credential_id=data["credential_id"],
            url=data["url"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "issuing_organization": self.issuing_organization,
            "issue_date": self.issue_date,
            "expiration_date": self.expiration_date,
            "credential_id": self.credential_id,
            "url": self.url,
        }


@dataclass
class Award:
    name: str
    type: str
    location: str
    date: str
    description: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Award":
        return Award(
            name=data["name"],
            type=data["type"],
            location=data["location"],
            date=data["date"],
            description=data["description"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "date": self.date,
            "description": self.description,
        }


@dataclass
class ExtracurricularAchievement:
    name: str
    type: str
    location: str
    date: str
    description: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExtracurricularAchievement":
        return ExtracurricularAchievement(
            name=data["name"],
            type=data["type"],
            location=data["location"],
            date=data["date"],
            description=data["description"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "date": self.date,
            "description": self.description,
        }


@dataclass
class Language:
    language: str
    proficiency: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Language":
        return Language(
            language=data["language"],
            proficiency=data["proficiency"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"language": self.language, "proficiency": self.proficiency}


@dataclass
class Resume:
    personal_information: PersonalInformation
    summary: str
    experiences: List[Experience]
    education: List[Education]
    skills: List[Skill]
    projects: List[Project]
    certifications: List[Certification]
    awards: List[Award]
    extracurricular_achievements: List[ExtracurricularAchievement]
    languages: List[Language]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Resume":
        return Resume(
            personal_information=PersonalInformation.from_dict(data["personal_information"]),
            summary=data.get("summary", ""),
            experiences=[Experience.from_dict(x) for x in data.get("experiences", [])],
            education=[Education.from_dict(x) for x in data.get("education", [])],
            skills=[Skill.from_dict(x) for x in data.get("skills", [])],
            projects=[Project.from_dict(x) for x in data.get("projects", [])],
            certifications=[Certification.from_dict(x) for x in data.get("certifications", [])],
            awards=[Award.from_dict(x) for x in data.get("awards", [])],
            extracurricular_achievements=[
                ExtracurricularAchievement.from_dict(x)
                for x in data.get("extracurricular/achievements", [])
            ],
            languages=[Language.from_dict(x) for x in data.get("languages", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "personal_information": self.personal_information.to_dict(),
            "summary": self.summary,
            "experiences": [e.to_dict() for e in self.experiences],
            "education": [e.to_dict() for e in self.education],
            "skills": [s.to_dict() for s in self.skills],
            "projects": [p.to_dict() for p in self.projects],
            "certifications": [c.to_dict() for c in self.certifications],
            "awards": [a.to_dict() for a in self.awards],
            "extracurricular/achievements": [ea.to_dict() for ea in self.extracurricular_achievements],
            "languages": [l.to_dict() for l in self.languages],
        }

    @staticmethod
    def from_json(json_str: str) -> "Resume":
        data = json.loads(json_str)
        return Resume.from_dict(data)

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), **kwargs)
