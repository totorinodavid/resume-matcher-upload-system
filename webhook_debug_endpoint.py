
# STRIPE WEBHOOK DEBUG ENDPOINT
# Fügen Sie diese Route zu webhooks.py hinzu für besseres Debugging

@router.post("/stripe/debug")
async def debug_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Debug-Endpoint für Stripe Webhook Probleme"""
    
    try:
        body = await request.body()
        stripe_signature = request.headers.get("stripe-signature", "")
        
        # Log raw webhook data
        logger.info(f"🔍 Debug Webhook Raw Body: {body[:500]}...")
        logger.info(f"🔍 Debug Webhook Headers: {dict(request.headers)}")
        
        # Try to parse as Stripe event
        try:
            event = stripe.Webhook.construct_event(
                body, stripe_signature, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            logger.info(f"✅ Debug Webhook Event Type: {event['type']}")
            logger.info(f"✅ Debug Webhook Event Data: {json.dumps(event['data'], indent=2)}")
            
            # If checkout.session.completed, test user resolution
            if event["type"] == "checkout.session.completed":
                session_obj = event["data"]["object"]
                
                # Test user resolution
                webhook_service = StripeWebhookService(db)
                user_id = await webhook_service._resolve_user_id(session_obj)
                
                return {
                    "debug_status": "success",
                    "event_type": event["type"],
                    "user_id_resolved": user_id,
                    "metadata": session_obj.get("metadata", {}),
                    "customer": session_obj.get("customer"),
                    "session_id": session_obj.get("id")
                }
            
        except Exception as e:
            logger.error(f"❌ Debug Webhook Parse Error: {e}")
            return {
                "debug_status": "parse_error",
                "error": str(e),
                "raw_body_length": len(body),
                "headers": dict(request.headers)
            }
            
    except Exception as e:
        logger.error(f"❌ Debug Webhook Critical Error: {e}")
        return {"debug_status": "critical_error", "error": str(e)}
