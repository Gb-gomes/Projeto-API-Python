from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session  
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(id_usuario, time_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + time_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_encode = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_encode
 
def auth_user(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False    
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario


@auth_router.get("/")
async def home():
    """
    Está é a rota padrão de autenticação. Apenas usuarios autenticados eram poder entrar no sistema. 
    """
    return{"mensagem":"Você logou com sucesso", "autenticado": False}



@auth_router.post("/criar-conta")
async def criar_conta(usuario_shema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_shema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email do usuario já foi cadastrado!")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_shema.senha)
        novo_usuario = Usuario(usuario_shema.nome, usuario_shema.email, senha_criptografada, usuario_shema.ativo, usuario_shema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"Usuario cadastrado com sucesso! Nome do usuario(a): {usuario_shema.nome}"}

    

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = auth_user(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais inválidas")
    else:
        access_token = create_token(usuario.id)
        refresh_token = create_token(usuario.id, time_token=timedelta(days=7))
        return{
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
               }
    

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends() , session: Session = Depends(pegar_sessao)):
    usuario = auth_user(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais inválidas")
    else:
        access_token = create_token(usuario.id)
        return{
                "access_token": access_token,
                "token_type": "Bearer"
               }



@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = create_token(usuario.id)
    return{
            "access_token": access_token,
            "token_type": "Bearer"
          }
