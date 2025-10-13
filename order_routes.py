from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    """
    Funcionalidade: Criação dos pedidos da pizzaria.    
    """
    return {"mensagem": "Você acessou a rota de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)): 
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido:int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Voê não tem autorização para fazer essa modificação")
    pedido.status = "CANCELADO"
    session.commit()
    return{
        "mensagem":f"pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido 
    }

@order_router.get("/listar")
async def listar_pedido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa requisiçã")
    else:
        pedidos = session.query(Pedido).all()
        return{
            "pedidos": pedidos
        }
    
@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, 
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(pegar_sessao),
                                usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existe")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Voê não tem autorização para fazer essa modificação")
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem":"item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,  
                                session: Session = Depends(pegar_sessao),
                                usuario: Usuario = Depends(verificar_token)):

    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no pedido não existe")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Voê não tem autorização para fazer essa modificação")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem":"Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens), 
        "pedido":pedido
    }

# finalizar o pedido  
@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido:int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Voê não tem autorização para fazer essa modificação")
    pedido.status = "FINALIZADO"
    session.commit()
    return{
        "mensagem":f"pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido 
    }

# Vizualizar 1 unico pedido 
@order_router.get("/pedido/{id_pedido}")
async def vizualizar_pedido(id_pedido:int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Voê não tem autorização para fazer essa modificação")
    return{
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

#Vizualizar todos os pedidos de um usuario
@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
    return pedidos 